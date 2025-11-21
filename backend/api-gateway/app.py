from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import httpx
import time
import logging
from typing import Dict, Any
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Resume Analysis API Gateway",
    description="Микросервисная система анализа резюме - API Gateway",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS настройки для dev режима
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Безопасность хостов (dev режим)
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "0.0.0.0"]
)

# Конфигурация микросервисов (dev)
SERVICES_CONFIG = {
    "auth": {
        "url": "http://localhost:8001",
        "prefix": "/api/v1/auth"
    },
    "email": {
        "url": "http://localhost:8002", 
        "prefix": "/api/v1/emails"
    },
    "resume": {
        "url": "http://localhost:8003",
        "prefix": "/api/v1/resumes"
    },
    "analysis": {
        "url": "http://localhost:8004",
        "prefix": "/api/v1/analysis"
    }
}

# Rate limiting storage (простая in-memory для dev)
rate_limit_store: Dict[str, list] = {}

def check_rate_limit(client_ip: str, limit: int = 6, window: int = 60) -> bool:
    """Простая rate limiting проверка для dev режима"""
    current_time = time.time()
    
    if client_ip not in rate_limit_store:
        rate_limit_store[client_ip] = []
    
    # Очищаем старые запросы
    rate_limit_store[client_ip] = [
        req_time for req_time in rate_limit_store[client_ip] 
        if current_time - req_time < window
    ]
    
    if len(rate_limit_store[client_ip]) >= limit:
        return False
    
    rate_limit_store[client_ip].append(current_time)
    return True

async def proxy_request(
    service_name: str, 
    path: str, 
    method: str, 
    request: Request
) -> Dict[str, Any]:
    """Проксирование запросов к микросервисам"""
    
    service_config = SERVICES_CONFIG.get(service_name)
    if not service_config:
        raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
    
    # Формируем URL для микросервиса
    service_url = f"{service_config['url']}{path}"
    
    # Подготавливаем данные запроса
    headers = dict(request.headers)
    headers.pop("host", None)  # Убираем host header
    
    body = None
    if method.upper() in ["POST", "PUT", "PATCH"]:
        body = await request.body()
    
    # Отправляем запрос к микросервису
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=method,
                url=service_url,
                headers=headers,
                content=body,
                params=request.query_params,
                timeout=30.0
            )
            
            return {
                "status_code": response.status_code,
                "content": response.content,
                "headers": dict(response.headers)
            }
            
        except httpx.RequestError as e:
            logger.error(f"Error proxying to {service_name}: {e}")
            raise HTTPException(
                status_code=503, 
                detail=f"Service {service_name} unavailable"
            )

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Логирование запросов"""
    start_time = time.time()
    
    # Rate limiting для polling запросов
    if "/api/v1/analysis/" in str(request.url) and request.method == "GET":
        client_ip = request.client.host if request.client else "unknown"
        if not check_rate_limit(client_ip, limit=6, window=60):
            raise HTTPException(
                status_code=429, 
                detail="Rate limit exceeded for polling"
            )
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    return response

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Resume Analysis API Gateway", 
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": list(SERVICES_CONFIG.keys()),
        "timestamp": time.time()
    }

# Подключаем маршруты
from routes.gateway import router as gateway_router
app.include_router(gateway_router)

# Тестовые endpoints для проверки авторизации
from middleware.auth import get_current_user_required, get_current_user_optional

@app.get("/api/v1/test/public")
async def test_public():
    """Публичный тестовый endpoint"""
    return {"message": "This is a public endpoint", "auth_required": False}

@app.get("/api/v1/test/protected")
async def test_protected(user=Depends(get_current_user_required)):
    """Защищенный тестовый endpoint"""
    return {
        "message": "This is a protected endpoint", 
        "auth_required": True,
        "user": user
    }

@app.get("/api/v1/test/optional")
async def test_optional(user=Depends(get_current_user_optional)):
    """Endpoint с опциональной авторизацией"""
    return {
        "message": "This endpoint has optional auth",
        "auth_required": False,
        "user": user,
        "authenticated": user is not None
    }
