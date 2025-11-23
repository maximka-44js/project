from fastapi import APIRouter, HTTPException, Depends, status, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
import uuid

from shared.database import DatabaseManager
from shared.auth import get_current_user_optional
from models.analysis import Analysis, AnalysisStatus
from tasks.analysis_tasks import process_raw_text_task, process_form_data_task


_db_manager = DatabaseManager("analysis")
log = logging.getLogger("analysis-routes")


def get_db():
    db = _db_manager.get_session()
    try:
        yield db
    finally:
        db.close()


router = APIRouter(tags=["analysis"])


# Pydantic схемы
class AnalysisStartRequest(BaseModel):
    upload_id: str
    email: Optional[EmailStr] = None


class PositionLevel(BaseModel):
    level: str
    salary_min: int
    salary_max: int
    currency: str
    confidence: float


class MarketData(BaseModel):
    total_vacancies_analyzed: int
    data_freshness_days: int
    location: str


class AnalysisResults(BaseModel):
    position_levels: List[PositionLevel]
    market_data: MarketData
    recommendations: Optional[List[str]] = None


class AnalysisResponseData(BaseModel):
    analysis_id: str
    status: str
    results: Optional[AnalysisResults] = None
    error_message: Optional[str] = None


class AnalysisResponse(BaseModel):
    data: AnalysisResponseData
    success: bool


class RawTextRequest(BaseModel):
    text: str = Field(
        ...,
        description="Текст резюме для анализа",
        min_length=10,
        max_length=10000
    )


class FormDataRequest(BaseModel):
    vacancy_nm: str = Field(..., description="Название вакансии")
    location: str = Field(..., description="Местоположение")
    schedule: str = Field(..., description="График работы")
    experience: str = Field(..., description="Опыт работы")
    work_hours: float = Field(..., description="Часы работы")
    skills_text: str = Field(..., description="Навыки и компетенции")


class SalaryPrediction(BaseModel):
    lowest_salary: float
    highest_salary: float
    currency: str


class ExtractedData(BaseModel):
    vacancy_nm: str
    location: str
    schedule: str
    experience: str
    work_hours: float
    skills_text: str


class RawTextAnalysisResult(BaseModel):
    extracted_data: ExtractedData
    salary_prediction: SalaryPrediction
    recommendations: str


class RawTextResponse(BaseModel):
    task_id: str
    success: bool
    message: str


class TaskResultResponse(BaseModel):
    success: bool
    result: Optional[RawTextAnalysisResult] = None
    error: Optional[str] = None
    status: str  # pending, success, failure


@router.post("/start", response_model=AnalysisResponse)
def start_analysis(
    request: AnalysisStartRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user_optional),
):
    """
    Запуск анализа резюме.
    Создает запись в БД и добавляет задачу в очередь.
    """
    log.info(f"Starting analysis for upload_id={request.upload_id}")

    try:
        # Проверка, нет ли уже анализа для этого upload_id
        existing = db.query(Analysis).filter(
            Analysis.upload_id == request.upload_id
        ).first()

        if existing:
            log.info(f"Analysis already exists: {existing.id}")
            return AnalysisResponse(
                data=AnalysisResponseData(
                    analysis_id=str(existing.id),
                    status=existing.status.value
                ),
                success=True
            )

        # Создание новой записи анализа
        analysis = Analysis(
            upload_id=request.upload_id,
            user_id=getattr(user, "id", None),
            email=request.email,
            status=AnalysisStatus.processing,
        )

        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        log.info(f"Analysis created: {analysis.id}")

        return AnalysisResponse(
            data=AnalysisResponseData(
                analysis_id=str(analysis.id),
                status=analysis.status.value
            ),
            success=True
        )

    except Exception as e:
        log.error(f"Error starting analysis: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start analysis"
        )


@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(
    analysis_id: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user_optional),
):
    """
    Получение статуса и результатов анализа.
    Используется для поллинга каждые 10 секунд.
    """
    try:
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()

        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found"
            )

        response_data = AnalysisResponseData(
            analysis_id=str(analysis.id),
            status=analysis.status.value
        )

        if analysis.status == AnalysisStatus.completed and analysis.results:
            response_data.results = AnalysisResults(**analysis.results)

        if analysis.status == AnalysisStatus.error:
            response_data.error_message = analysis.error_message

        return AnalysisResponse(
            data=response_data,
            success=analysis.status != AnalysisStatus.error
        )

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error getting analysis {analysis_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get analysis"
        )


@router.post("/webhook")
def analysis_webhook(
    analysis_id: str,
    results: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Internal webhook для обновления результатов анализа.
    Вызывается Celery worker'ом после завершения анализа.
    """
    log.info(f"Webhook called for analysis {analysis_id}")

    try:
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()

        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found"
            )

        if error:
            analysis.status = AnalysisStatus.error
            analysis.error_message = error
        else:
            analysis.status = AnalysisStatus.completed
            analysis.results = results

        analysis.completed_at = datetime.utcnow()
        db.commit()

        log.info(f"Analysis {analysis_id} updated: {analysis.status}")
        return {"success": True, "message": "Analysis updated"}

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error in webhook for {analysis_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update analysis"
        )


@router.post("/from_raw_text", response_model=RawTextResponse)
def analyze_raw_text(
    request: RawTextRequest,
    user=Depends(get_current_user_optional),
):
    """
    Анализ сырого текста резюме.
    
    Принимает текст резюме, извлекает структурированные данные,
    определяет profession_id и возвращает зарплатную вилку.
    
    Процесс выполняется асинхронно через Celery.
    """
    log.info(f"Starting raw text analysis")
    
    try:
        # Запускаем задачу Celery
        task = process_raw_text_task.delay(request.text)
        
        log.info(f"Raw text analysis task started: {task.id}")
        
        return RawTextResponse(
            task_id=task.id,
            success=True,
            message="Анализ текста запущен. Используйте task_id для получения результата."
        )
        
    except Exception as e:
        log.error(f"Error starting raw text analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start text analysis"
        )


@router.post("/from_form_data", response_model=RawTextResponse)
def analyze_form_data(
    vacancy_nm: str = Form(..., description="Название вакансии"),
    location: str = Form(..., description="Местоположение"),
    schedule: str = Form(..., description="График работы"),
    experience: str = Form(..., description="Опыт работы"),
    work_hours: float = Form(..., description="Часы работы"),
    skills_text: str = Form(..., description="Навыки и компетенции"),
    user=Depends(get_current_user_optional),
):
    """
    Анализ данных резюме из формы.
    
    Принимает структурированные данные резюме через form-data,
    определяет profession_id, возвращает зарплатную вилку и рекомендации от OpenAI.
    
    Процесс выполняется асинхронно через Celery.
    """
    log.info(f"Starting form data analysis")
    
    try:
        # Формируем словарь с данными формы
        form_data = {
            "vacancy_nm": vacancy_nm,
            "location": location,
            "schedule": schedule,
            "experience": experience,
            "work_hours": work_hours,
            "skills_text": skills_text
        }
        
        # Запускаем задачу Celery
        task = process_form_data_task.delay(form_data)
        
        log.info(f"Form data analysis task started: {task.id}")
        
        return RawTextResponse(
            task_id=task.id,
            success=True,
            message="Анализ данных формы запущен. Используйте task_id для получения результата."
        )
        
    except Exception as e:
        log.error(f"Error starting form data analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start form data analysis"
        )


@router.get("/task/{task_id}", response_model=TaskResultResponse)
def get_task_result(task_id: str):
    """
    Получение результата задачи по task_id.
    
    Используется для получения результата анализа сырого текста.
    """
    try:
        # Получаем статус задачи из Celery
        from celery.result import AsyncResult
        from celery_app import celery_app
        
        task_result = AsyncResult(task_id, app=celery_app)
        
        if task_result.ready():
            if task_result.successful():
                result_data = task_result.result
                if result_data.get("success"):
                    return TaskResultResponse(
                        success=True,
                        result=RawTextAnalysisResult(**result_data),
                        status="success"
                    )
                else:
                    return TaskResultResponse(
                        success=False,
                        error=result_data.get("error"),
                        status="failure"
                    )
            else:
                return TaskResultResponse(
                    success=False,
                    error=str(task_result.result),
                    status="failure"
                )
        else:
            return TaskResultResponse(
                success=True,
                status="pending"
            )
            
    except Exception as e:
        log.error(f"Error getting task result {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get task result"
        )