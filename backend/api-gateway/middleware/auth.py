from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional
import httpx
import os
import logging

logger = logging.getLogger(__name__)

# JWT настройки для dev
JWT_SECRET_KEY = "dev_jwt_secret_key_change_in_production"
JWT_ALGORITHM = "HS256"

# User Service URL
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8001")

security = HTTPBearer(auto_error=False)

class JWTAuth:
    """JWT аутентификация для API Gateway"""
    
    @staticmethod
    def verify_token_local(token: str) -> Optional[dict]:
        """Локальная проверка JWT токена"""
        try:
            payload = jwt.decode(
                token, 
                JWT_SECRET_KEY, 
                algorithms=[JWT_ALGORITHM]
            )
            return payload
        except JWTError:
            return None
    
    @staticmethod
    async def verify_token_with_user_service(token: str) -> Optional[dict]:
        """Проверка токена через User Service"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{USER_SERVICE_URL}/me",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    return {
                        "user_id": user_data["id"],
                        "email": user_data["email"],
                        "full_name": user_data.get("full_name"),
                        "is_active": user_data.get("is_active", True)
                    }
                return None
                
        except Exception as e:
            logger.error(f"Error verifying token with user service: {e}")
            return None

async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Optional[dict]:
    """Опциональная аутентификация - возвращает user или None"""
    if not credentials:
        return None
    
    # Сначала пробуем локальную проверку
    payload = JWTAuth.verify_token_local(credentials.credentials)
    if payload:
        return {
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            "full_name": payload.get("full_name")
        }
    
    # Если локальная не сработала, проверяем через User Service
    return await JWTAuth.verify_token_with_user_service(credentials.credentials)

async def get_current_user_required(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Обязательная аутентификация - выбрасывает 401 если нет токена"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await get_current_user_optional(credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

# Алиасы для удобства
require_auth = get_current_user_required
optional_auth = get_current_user_optional
