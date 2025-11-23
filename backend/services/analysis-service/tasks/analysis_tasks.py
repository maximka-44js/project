import time
import logging
import os
from celery import current_task
from celery_app import celery_app
from agents import Runner
from flows.extract_agent import extr_agent
from flows.get_proffession_id import get_profession_id
from flows.get_salary_prediction import get_salary_prediction
from openai import OpenAI

log = logging.getLogger(__name__)

TASKS_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(TASKS_DIR, 'data', 'professions.csv')
MODEL_PATH = os.path.join(TASKS_DIR, 'models', 'vector_matcher.pkl')
PREDICT_MODEL_PATH = os.path.join(TASKS_DIR, 'models', 'model_catboost_new_final.cbm')

def get_resume_recommendations(resume_text: str, extracted_data: dict) -> str:
    """
    Получает рекомендации по улучшению резюме от OpenAI API.
    
    Args:
        resume_text (str): Исходный текст резюме
        extracted_data (dict): Извлеченные структурированные данные
        
    Returns:
        str: Рекомендации по улучшению резюме
    """
    try:
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        prompt = f"""
Проанализируй следующее резюме и дай конкретные рекомендации по его улучшению:

ИСХОДНЫЙ ТЕКСТ РЕЗЮМЕ:
{resume_text}

ИЗВЛЕЧЕННЫЕ ДАННЫЕ:
- Вакансия: {extracted_data.get('vacancy_nm', 'Не указана')}
- Локация: {extracted_data.get('location', 'Не указана')}
- График работы: {extracted_data.get('schedule', 'Не указан')}
- Опыт работы: {extracted_data.get('experience', 'Не указан')}
- Часы работы: {extracted_data.get('work_hours', 'Не указано')}
- Навыки: {extracted_data.get('skills_text', 'Не указаны')}

Пожалуйста, предоставь конкретные рекомендации по улучшению этого резюме, сосредоточившись на:
1. Структуре и форматировании
2. Описании навыков и компетенций
3. Опыте работы и достижениях
4. Соответствии требованиям указанной вакансии
5. Общих рекомендациях по повышению привлекательности для работодателей

Отвечай на русском языке, кратко и по делу.
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты эксперт по составлению резюме и рекрутингу. Дай конкретные и практичные советы по улучшению резюме."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        recommendations = response.choices[0].message.content.strip()
        log.info(f"Successfully got recommendations from OpenAI: {len(recommendations)} characters")
        return recommendations
        
    except Exception as e:
        log.error(f"Error getting recommendations from OpenAI: {e}")
        return "Не удалось получить рекомендации. Проверьте настройки OpenAI API."

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
                model_path=PREDICT_MODEL_PATH,
                vacancy_id=str(profession_id),
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
        
        # Шаг 4: Получаем рекомендации по улучшению резюме от OpenAI
        log.info("=" * 50)
        log.info("STEP 4: Getting resume recommendations from OpenAI")
        log.info("=" * 50)
        
        try:
            extracted_data_dict = {
                "vacancy_nm": result.vacancy_nm,
                "location": result.location,
                "schedule": result.schedule,
                "experience": result.experience,
                "work_hours": result.work_hours,
                "skills_text": result.skills_text
            }
            
            log.info("Calling get_resume_recommendations...")
            recommendations = get_resume_recommendations(text, extracted_data_dict)
            log.info(f"STEP 4 SUCCESS: Got recommendations, length: {len(recommendations)} characters")
            
        except Exception as e:
            log.error(f"STEP 4 FAILED: Error in get_resume_recommendations")
            log.error(f"Error type: {type(e).__name__}")
            log.error(f"Error message: {str(e)}")
            log.error(f"Full error details:", exc_info=True)
            # Не прерываем выполнение задачи, если не удалось получить рекомендации
            recommendations = "Не удалось получить рекомендации по улучшению резюме."
        
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
            "salary_prediction": {
                "lowest_salary": lowest_salary,
                "highest_salary": highest_salary,
                "currency": "RUB"
            },
            "recommendations": recommendations
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


@celery_app.task(bind=True)
def process_form_data_task(self, form_data: dict):
    """
    Задача для обработки данных формы резюме.
    
    Выполняет следующие шаги:
    1. Получает profession_id по названию вакансии
    2. Вызывает get_salary_prediction для получения зарплатной вилки
    3. Получает рекомендации от OpenAI на основе структурированных данных
    
    Args:
        form_data (dict): Структурированные данные формы резюме
        
    Returns:
        dict: Результат с зарплатной вилкой и рекомендациями
    """
    try:
        log.info(f"Starting form data processing task {self.request.id}")
        log.info(f"Form data keys: {list(form_data.keys())}")
        
        # Шаг 1: Получаем profession_id по названию вакансии
        log.info("=" * 50)
        log.info("STEP 1: Getting profession_id")
        log.info("=" * 50)
        
        try:
            vacancy_nm = form_data.get('vacancy_nm')
            log.info(f"Calling get_profession_id with vacancy_nm: '{vacancy_nm}'")
            log.info(f"Using data_path: {DATA_PATH}")
            log.info(f"Using model_path: {MODEL_PATH}")
            log.info(f"Data file exists: {os.path.exists(DATA_PATH)}")
            log.info(f"Model file exists: {os.path.exists(MODEL_PATH)}")
            profession_id = get_profession_id(data_path=DATA_PATH, model_path=MODEL_PATH, profession_name=vacancy_nm)
            log.info(f"STEP 1 SUCCESS: Profession ID: {profession_id}")
        except Exception as e:
            log.error(f"STEP 1 FAILED: Error in get_profession_id")
            log.error(f"Error type: {type(e).__name__}")
            log.error(f"Error message: {str(e)}")
            log.error(f"Full error details:", exc_info=True)
            raise
        
        # Шаг 2: Получаем зарплатную вилку
        log.info("=" * 50)
        log.info("STEP 2: Getting salary prediction")
        log.info("=" * 50)
        
        try:
            log.info(f"Calling get_salary_prediction with parameters:")
            log.info(f"  vacancy_id: {profession_id}")
            log.info(f"  location: {form_data.get('location')}")
            log.info(f"  schedule: {form_data.get('schedule')}")
            log.info(f"  experience: {form_data.get('experience')}")
            log.info(f"  work_hours: {form_data.get('work_hours')}")
            log.info(f"  skills_text: {form_data.get('skills_text', '')[:100]}...")
            
            lowest_salary, highest_salary = get_salary_prediction(
                model_path=PREDICT_MODEL_PATH,
                vacancy_id=str(profession_id),
                location=form_data.get('location'),
                schedule=form_data.get('schedule'),
                experience=form_data.get('experience'),
                work_hours=form_data.get('work_hours'),
                skills_text=form_data.get('skills_text')
            )
            
            log.info(f"STEP 2 SUCCESS: Salary range: {lowest_salary} - {highest_salary}")
            
        except Exception as e:
            log.error(f"STEP 2 FAILED: Error in get_salary_prediction")
            log.error(f"Error type: {type(e).__name__}")
            log.error(f"Error message: {str(e)}")
            log.error(f"Full error details:", exc_info=True)
            raise
        
        # Шаг 3: Получаем рекомендации по улучшению резюме от OpenAI
        log.info("=" * 50)
        log.info("STEP 3: Getting resume recommendations from OpenAI")
        log.info("=" * 50)
        
        try:
            # Формируем текстовое представление резюме для OpenAI
            resume_text = f"""
Вакансия: {form_data.get('vacancy_nm')}
Местоположение: {form_data.get('location')}
График работы: {form_data.get('schedule')}
Опыт работы: {form_data.get('experience')}
Часы работы: {form_data.get('work_hours')}
Навыки и компетенции: {form_data.get('skills_text')}
"""
            
            log.info("Calling get_resume_recommendations...")
            recommendations = get_resume_recommendations(resume_text, form_data)
            log.info(f"STEP 3 SUCCESS: Got recommendations, length: {len(recommendations)} characters")
            
        except Exception as e:
            log.error(f"STEP 3 FAILED: Error in get_resume_recommendations")
            log.error(f"Error type: {type(e).__name__}")
            log.error(f"Error message: {str(e)}")
            log.error(f"Full error details:", exc_info=True)
            # Не прерываем выполнение задачи, если не удалось получить рекомендации
            recommendations = "Не удалось получить рекомендации по улучшению резюме."
        
        # Формируем результат
        log.info("=" * 50)
        log.info("FINAL STEP: Forming result")
        log.info("=" * 50)
        
        task_result = {
            "success": True,
            "extracted_data": {
                "vacancy_nm": form_data.get('vacancy_nm'),
                "location": form_data.get('location'),
                "schedule": form_data.get('schedule'),
                "experience": form_data.get('experience'),
                "work_hours": form_data.get('work_hours'),
                "skills_text": form_data.get('skills_text')
            },
            "salary_prediction": {
                "lowest_salary": lowest_salary,
                "highest_salary": highest_salary,
                "currency": "RUB"
            },
            "recommendations": recommendations
        }
        
        log.info(f"Task {self.request.id} completed successfully")
        log.info(f"Final result keys: {list(task_result.keys())}")
        return task_result
        
    except Exception as e:
        error_msg = str(e)
        if isinstance(error_msg, bytes):
            error_msg = error_msg.decode('utf-8', errors='replace')
        
        log.error("=" * 60)
        log.error("FORM DATA TASK FAILED WITH CRITICAL ERROR")
        log.error("=" * 60)
        log.error(f"Task ID: {self.request.id}")
        log.error(f"Error type: {type(e).__name__}")
        log.error(f"Error message: {error_msg}")
        log.error("Full traceback:", exc_info=True)
        
        import traceback
        tb_str = traceback.format_exc()
        log.error(f"Detailed traceback:\n{tb_str}")
        
        return {
            "success": False,
            "error": error_msg,
            "error_type": type(e).__name__,
            "traceback": tb_str
        }


# Здесь будут настоящие задачи для анализа резюме
# Примеры задач удалены для продакшена