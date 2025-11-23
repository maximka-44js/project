from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os

# JWT настройки для dev режима
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev_secret_key_123") 
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

class AuthUtils:
    """Утилиты для аутентификации"""
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Создание access токена"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """Создание refresh токена"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    @staticmethod
    def verify_token(token: str, expected_type: str = "access") -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            token_type = payload.get("type")
            if token_type != expected_type:
                return None

            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
                return None

            return payload
        except JWTError:
            return None
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Хеширование пароля"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def generate_tokens(user_data: Dict[str, Any]) -> Dict[str, str]:
        """Генерация пары токенов"""
        access_token = AuthUtils.create_access_token(user_data)
        refresh_token = AuthUtils.create_refresh_token(user_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }





# FastAPI dependencies для аутентификации
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)


def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
):
    """
    Опциональная аутентификация - возвращает user или None.
    Используется в эндпоинтах где аутентификация желательна но не обязательна.
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    payload = AuthUtils.verify_token(token, expected_type="access")
    
    if not payload:
        return None
    
    # Возвращаем минимальный объект user (можно расширить)
    class User:
        def __init__(self, user_id: str, email: str = None):
            self.id = user_id
            self.email = email
    
    return User(user_id=payload.get("sub"), email=payload.get("email"))


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Обязательная аутентификация - требует валидный токен.
    Возвращает user или выбрасывает 401.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    payload = AuthUtils.verify_token(token, expected_type="access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    class User:
        def __init__(self, user_id: str, email: str = None):
            self.id = user_id
            self.email = email
    
    return User(user_id=payload.get("sub"), email=payload.get("email"))


