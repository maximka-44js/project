from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
import uuid

from shared.database import DatabaseManager
from shared.auth import get_current_user_optional
from models.analysis import Analysis, AnalysisStatus


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