from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional
import redis
import os

# JWT настройки для dev
JWT_SECRET_KEY = "dev_jwt_secret_key_change_in_production"
JWT_ALGORITHM = "HS256"

# Redis для blacklist токенов
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    db=1,  # Используем db=1 для JWT blacklist
    decode_responses=True
)

security = HTTPBearer(auto_error=False)

class JWTAuth:
    """JWT аутентификация для API Gateway"""
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """Проверка JWT токена"""
        try:
            # Проверяем blacklist
            if redis_client.get(f"blacklist:{token}"):
                return None
            
            # Декодируем токен
            payload = jwt.decode(
                token, 
                JWT_SECRET_KEY, 
                algorithms=[JWT_ALGORITHM]
            )
            return payload
            
        except JWTError:
            return None
    
    @staticmethod
    def get_current_user(credentials: HTTPAuthorizationCredentials = None) -> Optional[dict]:
        """Получение текущего пользователя из токена"""
        if not credentials:
            return None
        
        token = credentials.credentials
        payload = JWTAuth.verify_token(token)
        
        if not payload:
            return None
        
        return {
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            "exp": payload.get("exp")
        }

def require_auth(credentials: HTTPAuthorizationCredentials = security):
    """Декоратор для обязательной аутентификации"""
    user = JWTAuth.get_current_user(credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def optional_auth(credentials: HTTPAuthorizationCredentials = security):
    """Декоратор для опциональной аутентификации"""
    return JWTAuth.get_current_user(credentials)
