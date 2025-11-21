from pydantic_settings import BaseSettings
from typing import Optional
import os

class BaseConfig(BaseSettings):
    """Базовая конфигурация для всех сервисов"""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Database
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres_dev_password"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    
    # JWT
    JWT_SECRET_KEY: str = "dev_jwt_secret_key_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

class AuthServiceConfig(BaseConfig):
    """Конфигурация Auth Service"""
    
    # Service specific
    SERVICE_NAME: str = "auth-service"
    SERVICE_PORT: int = 8001
    DATABASE_NAME: str = "auth_db"
    DATABASE_USER: str = "auth_user"
    DATABASE_PASSWORD: str = "auth_dev_password"
    
    # OAuth2
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    
    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.DATABASE_NAME}"
        )

class EmailServiceConfig(BaseConfig):
    """Конфигурация Email Service"""
    
    # Service specific
    SERVICE_NAME: str = "email-service"
    SERVICE_PORT: int = 8002
    DATABASE_NAME: str = "emails_db"
    DATABASE_USER: str = "email_user"
    DATABASE_PASSWORD: str = "email_dev_password"
    
    # SMTP
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True
    SMTP_FROM_EMAIL: str = "noreply@resume-analysis.dev"
    
    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.DATABASE_NAME}"
        )

class ResumeServiceConfig(BaseConfig):
    """Конфигурация Resume Service"""
    
    # Service specific
    SERVICE_NAME: str = "resume-service"
    SERVICE_PORT: int = 8003
    DATABASE_NAME: str = "resumes_db"
    DATABASE_USER: str = "resume_user"
    DATABASE_PASSWORD: str = "resume_dev_password"
    
    # File storage
    STORAGE_TYPE: str = "minio"  # minio, s3, local
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minio_user"
    MINIO_SECRET_KEY: str = "minio_dev_password"
    MINIO_BUCKET: str = "resumes"
    MINIO_SECURE: bool = False
    
    # File limits
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: list = ["pdf", "doc", "docx", "txt"]
    
    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.DATABASE_NAME}"
        )

class AnalysisServiceConfig(BaseConfig):
    """Конфигурация Analysis Service"""
    
    # Service specific
    SERVICE_NAME: str = "analysis-service"
    SERVICE_PORT: int = 8004
    DATABASE_NAME: str = "analysis_db"
    DATABASE_USER: str = "analysis_user"
    DATABASE_PASSWORD: str = "analysis_dev_password"
    
    # RabbitMQ
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "rabbit_user"
    RABBITMQ_PASSWORD: str = "rabbit_dev_password"
    RABBITMQ_VHOST: str = "/"
    
    # AI/LLM
    LLM_PROVIDER: str = "openai"  # openai, anthropic, local
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Analysis settings
    ANALYSIS_TIMEOUT_MINUTES: int = 10
    MAX_CONCURRENT_ANALYSES: int = 5
    
    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.DATABASE_NAME}"
        )
    
    @property
    def rabbitmq_url(self) -> str:
        return (
            f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}"
            f"@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}{self.RABBITMQ_VHOST}"
        )

class GatewayConfig(BaseConfig):
    """Конфигурация API Gateway"""
    
    # Service specific
    SERVICE_NAME: str = "api-gateway"
    SERVICE_PORT: int = 8000
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 6
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    
    # Services endpoints
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    EMAIL_SERVICE_URL: str = "http://localhost:8002"
    RESUME_SERVICE_URL: str = "http://localhost:8003"
    ANALYSIS_SERVICE_URL: str = "http://localhost:8004"

# Factory functions для получения конфигураций
def get_auth_config() -> AuthServiceConfig:
    return AuthServiceConfig()

def get_email_config() -> EmailServiceConfig:
    return EmailServiceConfig()

def get_resume_config() -> ResumeServiceConfig:
    return ResumeServiceConfig()

def get_analysis_config() -> AnalysisServiceConfig:
    return AnalysisServiceConfig()

def get_gateway_config() -> GatewayConfig:
    return GatewayConfig()