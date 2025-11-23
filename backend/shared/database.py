import logging
import os
import time
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import MetaData, create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Базовые настройки для разных БД в dev режиме
DATABASE_CONFIGS = {
    "auth": {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": os.getenv("POSTGRES_PORT", "5432"),
        "database": "auth_db",
        "username": "auth_user",
        "password": "auth_dev_password"
    },
    "emails": {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": os.getenv("POSTGRES_PORT", "5432"),
        "database": "emails_db",
        "username": "email_user",
        "password": "email_dev_password"
    },
    "resumes": {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": os.getenv("POSTGRES_PORT", "5432"),
        "database": "resumes_db",
        "username": "resume_user",
        "password": "resume_dev_password"
    },
    "analysis": {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": os.getenv("POSTGRES_PORT", "5432"),
        "database": "analysis_db",
        "username": "analysis_user",
        "password": "analysis_dev_password"
    }
}

# Базовый класс для моделей
Base = declarative_base()

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Менеджер подключений к базам данных"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.config = DATABASE_CONFIGS.get(service_name)
        
        if not self.config:
            raise ValueError(f"Unknown service: {service_name}")
        
        # Создание URL подключения
        self.database_url = (
            f"postgresql://{self.config['username']}:{self.config['password']}"
            f"@{self.config['host']}:{self.config['port']}/{self.config['database']}"
        )
        
        # Создание engine и session factory
        self.engine = create_engine(
            self.database_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            echo=os.getenv("SQL_DEBUG", "false").lower() == "true"
        )
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        self.metadata = MetaData()
    
    def get_session(self):
        """Получение сессии БД"""
        return self.SessionLocal()
    
    @contextmanager
    def get_db(self) -> Generator:
        """Контекстный менеджер для работы с БД"""
        db = self.SessionLocal()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
    
    def create_tables(self, retries: int | None = None, retry_interval: float | None = None):
        """Создание таблиц с ожиданием готовности БД"""
        max_retries = retries if retries is not None else int(os.getenv("DB_INIT_RETRIES", "10"))
        interval = retry_interval if retry_interval is not None else float(os.getenv("DB_INIT_RETRY_INTERVAL", "3"))

        attempt = 0
        while True:
            try:
                Base.metadata.create_all(bind=self.engine)
                if attempt:
                    logger.info(
                        "Tables for service %s created after %d retries", self.service_name, attempt
                    )
                return
            except OperationalError as exc:
                attempt += 1
                if attempt > max_retries:
                    logger.error(
                        "Unable to create tables for service %s after %d attempts: %s",
                        self.service_name,
                        attempt - 1,
                        exc,
                    )
                    raise

                logger.warning(
                    "create_tables attempt %d/%d failed for service %s: %s. Retrying in %.1f seconds",
                    attempt,
                    max_retries,
                    self.service_name,
                    exc,
                    interval,
                )
                time.sleep(interval)
    
    def drop_tables(self):
        """Удаление таблиц (только для dev!)"""
        if os.getenv("ENVIRONMENT", "dev") == "dev":
            Base.metadata.drop_all(bind=self.engine)

# Функция для FastAPI dependency injection
def get_database_manager(service_name: str):
    """Factory function для создания DatabaseManager"""
    return DatabaseManager(service_name)

# Dependency для FastAPI
def get_db_session(service_name: str):
    """Dependency для получения сессии БД в FastAPI"""
    db_manager = DatabaseManager(service_name)
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()
