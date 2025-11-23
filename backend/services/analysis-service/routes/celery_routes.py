from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Any
import logging

from celery_app import celery_app

log = logging.getLogger(__name__)
router = APIRouter(tags=["celery"])


# Pydantic схемы для API
class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Any] = None
    meta: Optional[dict] = None
    error: Optional[str] = None


@router.get("/status")
def get_celery_status():
    """Проверка статуса Celery"""
    try:
        # Проверяем доступность Celery
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        active = inspect.active()
        
        if stats is None:
            return {"status": "error", "message": "Celery workers недоступны"}
        
        return {
            "status": "ok",
            "message": "Celery работает",
            "workers": list(stats.keys()) if stats else [],
            "active_tasks": sum(len(tasks) for tasks in active.values()) if active else 0
        }
    except Exception as e:
        log.error(f"Ошибка при проверке статуса Celery: {e}")
        return {"status": "error", "message": str(e)}


# Тестовые эндпоинты удалены
# Здесь будут реальные эндпоинты для запуска задач анализа


@router.get("/status/{task_id}", response_model=TaskStatusResponse)
def get_task_status(task_id: str):
    """Получение статуса задачи по ID"""
    try:
        task_result = celery_app.AsyncResult(task_id)
        
        if task_result.state == 'PENDING':
            response = TaskStatusResponse(
                task_id=task_id,
                status='pending',
                result=None,
                meta=None
            )
        elif task_result.state == 'PROGRESS':
            response = TaskStatusResponse(
                task_id=task_id,
                status='progress',
                result=None,
                meta=task_result.info
            )
        elif task_result.state == 'SUCCESS':
            response = TaskStatusResponse(
                task_id=task_id,
                status='success',
                result=task_result.result,
                meta=None
            )
        elif task_result.state == 'FAILURE':
            response = TaskStatusResponse(
                task_id=task_id,
                status='failure',
                result=None,
                meta=None,
                error=str(task_result.info)
            )
        else:
            response = TaskStatusResponse(
                task_id=task_id,
                status=task_result.state.lower(),
                result=task_result.result,
                meta=task_result.info if hasattr(task_result, 'info') else None
            )
        
        return response
        
    except Exception as e:
        log.error(f"Ошибка при получении статуса задачи {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cancel/{task_id}")
def cancel_task(task_id: str):
    """Отмена задачи по ID"""
    try:
        celery_app.control.revoke(task_id, terminate=True)
        return {
            "task_id": task_id,
            "status": "cancelled",
            "message": f"Задача {task_id} отменена"
        }
    except Exception as e:
        log.error(f"Ошибка при отмене задачи {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workers")
def get_workers_info():
    """Получение информации о воркерах"""
    try:
        inspect = celery_app.control.inspect()
        
        stats = inspect.stats() or {}
        active = inspect.active() or {}
        scheduled = inspect.scheduled() or {}
        
        workers_info = []
        for worker_name in stats.keys():
            worker_stats = stats.get(worker_name, {})
            worker_active = active.get(worker_name, [])
            worker_scheduled = scheduled.get(worker_name, [])
            
            workers_info.append({
                "name": worker_name,
                "status": "online",
                "active_tasks": len(worker_active),
                "scheduled_tasks": len(worker_scheduled),
                "processed_tasks": worker_stats.get("total", {}).get("tasks.analysis_tasks.simple_test_task", 0),
                "pool": worker_stats.get("pool", {}).get("max-concurrency", "unknown")
            })
        
        return {
            "workers": workers_info,
            "total_workers": len(workers_info)
        }
        
    except Exception as e:
        log.error(f"Ошибка при получении информации о воркерах: {e}")
        return {
            "workers": [],
            "total_workers": 0,
            "error": str(e)
        }


@router.get("/queues")
def get_queues_info():
    """Получение информации об очередях"""
    try:
        inspect = celery_app.control.inspect()
        active_queues = inspect.active_queues() or {}
        
        queues_info = []
        for worker_name, queues in active_queues.items():
            for queue in queues:
                queues_info.append({
                    "worker": worker_name,
                    "name": queue["name"],
                    "exchange": queue.get("exchange", {}).get("name", ""),
                    "routing_key": queue.get("routing_key", "")
                })
        
        return {
            "queues": queues_info,
            "total_queues": len(set(q["name"] for q in queues_info))
        }
        
    except Exception as e:
        log.error(f"Ошибка при получении информации об очередях: {e}")
        return {
            "queues": [],
            "total_queues": 0,
            "error": str(e)
        }