from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import sys
import os
from datetime import datetime
import logging

# Добавляем путь к shared модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.database import DatabaseManager
from models.user import User
import hashlib
import secrets
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import timedelta

# Простые утилиты для хеширования и JWT
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_SECRET = "dev_secret_key_123"
JWT_ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token: str, expected_type: str = "access"):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != expected_type:
            return None
        return payload
    except JWTError:
        return None

# Локальные схемы для этого сервиса
class UserRegisterRequest(BaseModel):
    email: EmailStr = Field(..., description="Email пользователя", example="user@example.com")
    password: str = Field(..., min_length=6, description="Пароль (минимум 6 символов)", example="password123")
    full_name: Optional[str] = Field(None, description="Полное имя пользователя", example="Иван Иванов")

class UserLoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Email пользователя", example="user@example.com")
    password: str = Field(..., description="Пароль", example="password123")

class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh токен")

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900
    user: UserResponse

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создание приложения
app = FastAPI(
    title="User Service",
    description="Сервис управления пользователями и аутентификации",
    version="1.0.0"
)

# Database manager
db_manager = DatabaseManager("auth")
db_manager.create_tables()  
security = HTTPBearer(auto_error=False)

def get_db():
    """Dependency для получения сессии БД"""
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Получение текущего пользователя из JWT токена"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token required"
        )
    
    # Проверяем токен
    payload = verify_token(credentials.credentials, "access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Получаем пользователя из БД
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled"
        )
    
    return user

@app.get("/")
async def root():
    """Health check"""
    return {"service": "User Service", "status": "healthy"}

@app.post("/register", response_model=TokenResponse)
async def register(
    user_data: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """Регистрация нового пользователя"""
    email = user_data.email.lower().strip()
    password = user_data.password
    full_name = user_data.full_name or ""
    
    # Pydantic уже провалидировал данные
    
    # Проверяем, не существует ли уже пользователь
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Создаем нового пользователя
    try:
        new_user = User(
            email=email,
            full_name=full_name,
            is_active=True,
            is_verified=False
        )
        new_user.hashed_password = hash_password(password)
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Генерируем токены
        token_data = {
            "sub": str(new_user.id),
            "email": new_user.email,
            "full_name": new_user.full_name
        }
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        logger.info(f"New user registered: {email}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse(
                id=new_user.id,
                email=new_user.email,
                full_name=new_user.full_name,
                is_active=new_user.is_active,
                created_at=new_user.created_at
            )
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@app.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """Вход пользователя"""
    email = credentials.email.lower().strip()
    password = credentials.password
    
    # Pydantic уже провалидировал данные
    
    # Находим пользователя
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Проверяем пароль
    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Проверяем активность аккаунта
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled"
        )
    
    # Обновляем время последнего входа
    try:
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Генерируем токены
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "full_name": user.full_name
        }
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        logger.info(f"User logged in: {email}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Login update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@app.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Получение информации о текущем пользователе"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )

@app.post("/refresh", response_model=dict)
async def refresh_token(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Обновление access токена с помощью refresh токена"""
    
    # Проверяем refresh токен
    payload = verify_token(token_data.refresh_token, "refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Получаем пользователя
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Генерируем новый access токен
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "full_name": user.full_name
    }
    new_access_token = create_access_token(token_data)
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "expires_in": 900  # 15 минут
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
