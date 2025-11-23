import time
import logging
import os
from celery import current_task
from celery_app import celery_app
from agents import Runner
from flows.extract_agent import extr_agent
from flows.get_proffession_id import get_profession_id
from flows.get_salary_prediction import get_salary_prediction

log = logging.getLogger(__name__)

TASKS_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(TASKS_DIR, 'data', 'professions.csv')
MODEL_PATH = os.path.join(TASKS_DIR, 'models', 'vector_matcher.pkl')


@celery_app.task(bind=True)
def process_raw_text_task(self, text: str):
    """
    Задача для обработки сырого текста резюме.
    
    Выполняет следующие шаги:
    1. Извлекает структурированные данные из текста с помощью extr_agent
    2. Получает profession_id по названию вакансии
    3. Вызывает get_salary_prediction для получения зарплатной вилки
    
    Args:
        text (str): Текст резюме для обработки
        
    Returns:
        dict: Результат с зарплатной вилкой и дополнительной информацией
    """
    try:
        # Убеждаемся что текст правильно обрабатывается как UTF-8
        if isinstance(text, bytes):
            text = text.decode('utf-8')
        
        log.info(f"Starting text processing task {self.request.id}")
        log.info(f"Text length: {len(text)} characters")
        log.info(f"Text preview (first 200 chars): {text[:200]}")
        
        # Шаг 1: Извлекаем структурированные данные из текста
        log.info("=" * 50)
        log.info("STEP 1: Starting extraction of structured data from text")
        log.info("=" * 50)
        
        try:
            log.info("Calling Runner.run_sync(extr_agent, text)...")
            mez_result = Runner.run_sync(extr_agent, text)
            result = mez_result.final_output
            log.info(f"STEP 1 SUCCESS: Runner.run_sync completed, result type: {type(result)}")
            
            if not result:
                raise ValueError("Failed to extract data from text - result is None or empty")
            
            # Детальное логирование результата
            log.info(f"Extracted result attributes:")
            for attr in ['vacancy_nm', 'location', 'schedule', 'experience', 'work_hours', 'skills_text']:
                try:
                    value = getattr(result, attr)
                    log.info(f"  {attr}: {value}")
                except AttributeError as e:
                    log.warning(f"  {attr}: MISSING ATTRIBUTE - {e}")
                    
        except Exception as e:
            log.error(f"STEP 1 FAILED: Error in Runner.run_sync or extr_agent")
            log.error(f"Error type: {type(e).__name__}")
            log.error(f"Error message: {str(e)}")
            log.error(f"Full error details:", exc_info=True)
            raise
        
        # Шаг 2: Получаем profession_id по названию вакансии
        log.info("=" * 50)
        log.info("STEP 2: Getting profession_id")
        log.info("=" * 50)
        
        try:
            log.info(f"Calling get_profession_id with vacancy_nm: '{result.vacancy_nm}'")
            log.info(f"Using data_path: {DATA_PATH}")
            log.info(f"Using model_path: {MODEL_PATH}")
            log.info(f"Data file exists: {os.path.exists(DATA_PATH)}")
            log.info(f"Model file exists: {os.path.exists(MODEL_PATH)}")
            profession_id = get_profession_id(data_path=DATA_PATH, model_path=MODEL_PATH, profession_name=result.vacancy_nm)
            log.info(f"STEP 2 SUCCESS: Profession ID: {profession_id}")
        except Exception as e:
            log.error(f"STEP 2 FAILED: Error in get_profession_id")
            log.error(f"Error type: {type(e).__name__}")
            log.error(f"Error message: {str(e)}")
            log.error(f"Full error details:", exc_info=True)
            raise
        
        # Шаг 3: Получаем зарплатную вилку
        log.info("=" * 50)
        log.info("STEP 3: Getting salary prediction")
        log.info("=" * 50)
        
        try:
            log.info(f"Calling get_salary_prediction with parameters:")
            log.info(f"  vacancy_id: {profession_id}")
            log.info(f"  location: {result.location}")
            log.info(f"  schedule: {result.schedule}")
            log.info(f"  experience: {result.experience}")
            log.info(f"  work_hours: {result.work_hours}")
            log.info(f"  skills_text: {result.skills_text[:100] if result.skills_text else 'None'}...")
            
            lowest_salary, highest_salary = get_salary_prediction(
                vacancy_id=profession_id,
                location=result.location,
                schedule=result.schedule,
                experience=result.experience,
                work_hours=result.work_hours,
                skills_text=result.skills_text
            )
            
            log.info(f"STEP 3 SUCCESS: Salary range: {lowest_salary} - {highest_salary}")
            
        except Exception as e:
            log.error(f"STEP 3 FAILED: Error in get_salary_prediction")
            log.error(f"Error type: {type(e).__name__}")
            log.error(f"Error message: {str(e)}")
            log.error(f"Full error details:", exc_info=True)
            raise
        
        # Формируем результат
        log.info("=" * 50)
        log.info("FINAL STEP: Forming result")
        log.info("=" * 50)
        
        task_result = {
            "success": True,
            "extracted_data": {
                "vacancy_nm": result.vacancy_nm,
                "location": result.location,
                "schedule": result.schedule,
                "experience": result.experience,
                "work_hours": result.work_hours,
                "skills_text": result.skills_text
            },
            "profession_id": profession_id,
            "salary_prediction": {
                "lowest_salary": lowest_salary,
                "highest_salary": highest_salary,
                "currency": "RUB"
            }
        }
        
        log.info(f"Task {self.request.id} completed successfully")
        log.info(f"Final result keys: {list(task_result.keys())}")
        return task_result
        
    except Exception as e:
        error_msg = str(e)
        # Обеспечиваем что сообщение об ошибке тоже правильно кодируется
        if isinstance(error_msg, bytes):
            error_msg = error_msg.decode('utf-8', errors='replace')
        
        log.error("=" * 60)
        log.error("TASK FAILED WITH CRITICAL ERROR")
        log.error("=" * 60)
        log.error(f"Task ID: {self.request.id}")
        log.error(f"Error type: {type(e).__name__}")
        log.error(f"Error message: {error_msg}")
        log.error("Full traceback:", exc_info=True)
        
        # Дополнительная информация для отладки
        import traceback
        tb_str = traceback.format_exc()
        log.error(f"Detailed traceback:\n{tb_str}")
        
        # Проверяем, содержит ли ошибка информацию о experimental_allow_partial
        if "experimental_allow_partial" in error_msg:
            log.error("DETECTED: experimental_allow_partial error - likely pydantic version issue")
            log.error("This error typically occurs in the data extraction/validation step")
        
        return {
            "success": False,
            "error": error_msg,
            "error_type": type(e).__name__,
            "traceback": tb_str
        }


# Здесь будут настоящие задачи для анализа резюме
# Примеры задач удалены для продакшена