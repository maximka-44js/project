from fastapi import APIRouter, Request, Depends, HTTPException
from middleware.auth import require_auth, optional_auth
import httpx
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Конфигурация сервисов
SERVICES = {
    "auth": "http://localhost:8001",
    "email": "http://localhost:8002", 
    "resume": "http://localhost:8003",
    "analysis": "http://localhost:8004"
}

async def proxy_to_service(service_name: str, path: str, request: Request):
    """Универсальное проксирование к сервисам"""
    service_url = SERVICES.get(service_name)
    if not service_url:
        raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
    
    # Подготовка запроса
    url = f"{service_url}{path}"
    headers = dict(request.headers)
    headers.pop("host", None)
    
    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        body = await request.body()
    
    # Отправка запроса
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=body,
                params=request.query_params,
                timeout=30.0
            )
            return response
        except httpx.RequestError as e:
            logger.error(f"Proxy error to {service_name}: {e}")
            raise HTTPException(status_code=503, detail=f"Service {service_name} unavailable")

# Auth Service Routes (публичные)
@router.api_route("/api/v1/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def auth_proxy(path: str, request: Request):
    """Проксирование к Auth Service"""
    response = await proxy_to_service("auth", f"/{path}", request)
    return response.json()

# Email Service Routes (публичные для подписки)
@router.api_route("/api/v1/emails/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def email_proxy(path: str, request: Request):
    """Проксирование к Email Service"""
    response = await proxy_to_service("email", f"/{path}", request)
    return response.json()

# Resume Service Routes (требуют аутентификации для upload)
@router.api_route("/api/v1/resumes/supported-formats", methods=["GET"])
async def resume_formats_proxy(request: Request):
    """Публичный endpoint - поддерживаемые форматы"""
    response = await proxy_to_service("resume", "/supported-formats", request)
    return response.json()

@router.api_route("/api/v1/resumes/{path:path}", methods=["POST", "PUT", "DELETE"])
async def resume_proxy_auth(path: str, request: Request, user=Depends(require_auth)):
    """Защищенные операции с резюме"""
    # Добавляем user_id в заголовки для сервиса
    headers = dict(request.headers)
    headers["X-User-ID"] = str(user["user_id"])
    
    response = await proxy_to_service("resume", f"/{path}", request)
    return response.json()

@router.api_route("/api/v1/resumes/{path:path}", methods=["GET"])
async def resume_proxy_optional(path: str, request: Request, user=Depends(optional_auth)):
    """GET запросы с опциональной аутентификацией"""
    headers = dict(request.headers)
    if user:
        headers["X-User-ID"] = str(user["user_id"])
    
    response = await proxy_to_service("resume", f"/{path}", request)
    return response.json()

# Analysis Service Routes
@router.api_route("/api/v1/analysis/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def analysis_proxy(path: str, request: Request, user=Depends(optional_auth)):
    """Проксирование к Analysis Service"""
    headers = dict(request.headers)
    if user:
        headers["X-User-ID"] = str(user["user_id"])
    
    response = await proxy_to_service("analysis", f"/{path}", request)
    return response.json()
