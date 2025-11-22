from fastapi import APIRouter, Request, Depends, HTTPException, Response
from middleware.auth import get_current_user_required, get_current_user_optional
import httpx
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Конфигурация сервисов
SERVICES = {
    "user": "http://localhost:8001",      # User Service (auth)
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

# User Service Routes (регистрация, логин - публичные)
@router.api_route("/auth/register", methods=["POST"])
async def auth_register_proxy(request: Request):
    """Проксирование регистрации к User Service"""
    response = await proxy_to_service("user", "/register", request)
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers)
    )

@router.api_route("/auth/login", methods=["POST"])
async def auth_login_proxy(request: Request):
    """Проксирование логина к User Service"""
    response = await proxy_to_service("user", "/login", request)
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers)
    )

@router.api_route("/auth/refresh", methods=["POST"])
async def auth_refresh_proxy(request: Request):
    """Проксирование обновления токена к User Service"""
    response = await proxy_to_service("user", "/refresh", request)
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers)
    )

# Защищенный маршрут для получения профиля
@router.api_route("/auth/me", methods=["GET"])
async def auth_me_proxy(request: Request, user=Depends(get_current_user_required)):
    """Получение профиля текущего пользователя"""
    response = await proxy_to_service("user", "/me", request)
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers)
    )

# Email Service Routes (публичные для подписки)
@router.api_route("/emails/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def email_proxy(path: str, request: Request):
    """Проксирование к Email Service"""
    response = await proxy_to_service("email", f"/{path}", request)
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers)
    )

# Resume Service Routes
@router.api_route("/resumes/supported-formats", methods=["GET"])
async def resume_formats_proxy(request: Request):
    """Публичный endpoint - поддерживаемые форматы"""
    response = await proxy_to_service("resume", "/supported-formats", request)
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers)
    )

@router.api_route("/resumes/{path:path}", methods=["POST", "PUT", "DELETE"])
async def resume_proxy_auth(path: str, request: Request, user=Depends(get_current_user_required)):
    """Защищенные операции с резюме"""
    response = await proxy_to_service("resume", f"/{path}", request)
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers)
    )

@router.api_route("/resumes/{path:path}", methods=["GET"])
async def resume_proxy_optional(path: str, request: Request, user=Depends(get_current_user_optional)):
    """GET запросы с опциональной аутентификацией"""
    response = await proxy_to_service("resume", f"/{path}", request)
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers)
    )

# Analysis Service Routes
@router.api_route("/analysis/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def analysis_proxy(path: str, request: Request, user=Depends(get_current_user_optional)):
    """Проксирование к Analysis Service"""
    response = await proxy_to_service("analysis", f"/{path}", request)
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers)
    )
