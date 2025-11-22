from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os

# JWT настройки для dev режима
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev_jwt_secret_key_change_in_production") 
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
        """Проверка токена"""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            
            # Проверяем тип токена
            token_type = payload.get("type")
            if token_type != expected_type:
                return None
            
            # Проверяем expiration
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

class OAuth2Config:
    """Конфигурация OAuth2 провайдеров"""
    
    # Google OAuth2
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/v1/auth/google/callback")
    
    # GitHub OAuth2  
    GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
    GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
    GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI", "http://localhost:8000/api/v1/auth/github/callback")
    
    @classmethod
    def get_google_oauth_url(cls) -> str:
        """URL для Google OAuth2"""
        base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        params = [
            f"client_id={cls.GOOGLE_CLIENT_ID}",
            f"redirect_uri={cls.GOOGLE_REDIRECT_URI}",
            "response_type=code",
            "scope=openid email profile",
            "access_type=offline"
        ]
        return f"{base_url}?{'&'.join(params)}"
    
    @classmethod
    def get_github_oauth_url(cls) -> str:
        """URL для GitHub OAuth2"""
        base_url = "https://github.com/login/oauth/authorize"
        params = [
            f"client_id={cls.GITHUB_CLIENT_ID}",
            f"redirect_uri={cls.GITHUB_REDIRECT_URI}",
            "scope=user:email"
        ]
        return f"{base_url}?{'&'.join(params)}"

# Константы для разных типов пользователей
class UserRole:
    """Роли пользователей"""
    USER = "user"
    ADMIN = "admin"
    
class AuthScope:
    """Области видимости"""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


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
