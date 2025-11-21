from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

# ================================
# Базовые схемы
# ================================

class BaseResponse(BaseModel):
    """Базовая схема ответа"""
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ErrorResponse(BaseResponse):
    """Схема ошибки"""
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

# ================================
# Auth схемы
# ================================

class UserBase(BaseModel):
    """Базовая схема пользователя"""
    email: EmailStr
    full_name: Optional[str] = None

class UserRegisterRequest(BaseModel):
    """Схема запроса регистрации"""
    email: EmailStr = Field(..., description="Email пользователя", example="user@example.com")
    password: str = Field(..., min_length=6, description="Пароль (минимум 6 символов)", example="password123")
    full_name: Optional[str] = Field(None, description="Полное имя пользователя", example="Иван Иванов")

class UserLoginRequest(BaseModel):
    """Схема запроса входа"""
    email: EmailStr = Field(..., description="Email пользователя", example="user@example.com")
    password: str = Field(..., description="Пароль", example="password123")

class UserCreate(UserBase):
    """Схема создания пользователя"""
    provider: str = Field(..., description="OAuth provider (google, github)")
    provider_id: str = Field(..., description="Provider user ID")

class UserResponse(UserBase):
    """Схема ответа с данными пользователя"""
    id: int
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """Схема ответа с токенами"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900  # 15 минут в секундах
    user: UserResponse

class RefreshTokenRequest(BaseModel):
    """Схема запроса обновления токена"""
    refresh_token: str

# ================================
# Email схемы
# ================================

class EmailSubscriptionRequest(BaseModel):
    """Схема подписки на email"""
    email: EmailStr
    
    @validator('email')
    def validate_email_domain(cls, v):
        """Простая валидация домена (для dev)"""
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v.lower()

class EmailSubscriptionResponse(BaseModel):
    """Схема ответа подписки"""
    email: EmailStr
    subscribed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class EmailStatusResponse(BaseModel):
    """Схема статуса email"""
    email: EmailStr
    subscribed: bool
    last_sent: Optional[datetime] = None

# ================================
# Resume схемы
# ================================

class SupportedFormatsResponse(BaseModel):
    """Поддерживаемые форматы файлов"""
    formats: List[str] = ["pdf", "doc", "docx", "txt"]
    max_size_mb: int = 10
    description: str = "Supported resume file formats"

class ResumeUploadResponse(BaseModel):
    """Ответ загрузки резюме"""
    resume_id: str
    filename: str
    file_size: int
    content_type: str
    uploaded_at: datetime
    processing_status: str = "uploaded"

class ResumeStatus(str, Enum):
    """Статусы обработки резюме"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    ERROR = "error"

class ResumeInfo(BaseModel):
    """Информация о резюме"""
    id: str
    filename: str
    file_size: int
    content_type: str
    status: ResumeStatus
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True

# ================================
# Analysis схемы
# ================================

class AnalysisStatus(str, Enum):
    """Статусы анализа"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class SalaryRange(BaseModel):
    """Диапазон зарплаты"""
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    currency: str = "RUB"
    confidence: Optional[float] = None

class AnalysisResult(BaseModel):
    """Результат анализа резюме"""
    analysis_id: str
    resume_id: str
    status: AnalysisStatus
    
    # Результаты анализа
    position: Optional[str] = None
    experience_years: Optional[int] = None
    skills: Optional[List[str]] = None
    education_level: Optional[str] = None
    
    # Зарплатные ожидания
    salary_expectations: Optional[SalaryRange] = None
    market_salary_range: Optional[SalaryRange] = None
    salary_recommendation: Optional[str] = None
    
    # Метаданные
    started_at: datetime
    completed_at: Optional[datetime] = None
    processing_time_seconds: Optional[int] = None
    
    class Config:
        from_attributes = True

class AnalysisStartRequest(BaseModel):
    """Запрос запуска анализа"""
    resume_id: str
    email: Optional[EmailStr] = None  # Для отправки результатов

class AnalysisStartResponse(BaseModel):
    """Ответ запуска анализа"""
    analysis_id: str
    resume_id: str
    status: AnalysisStatus = AnalysisStatus.PENDING
    estimated_time_minutes: int = 5

# ================================
# Gateway схемы
# ================================

class HealthResponse(BaseModel):
    """Схема health check"""
    status: str = "healthy"
    services: List[str]
    timestamp: float

class ServiceStatus(BaseModel):
    """Статус сервиса"""
    name: str
    url: str
    healthy: bool
    response_time_ms: Optional[float] = None
    last_check: datetime

class GatewayStatus(BaseModel):
    """Статус Gateway"""
    gateway_status: str = "healthy"
    services: List[ServiceStatus]
    total_requests: int = 0
    uptime_seconds: int = 0
