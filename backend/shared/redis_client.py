import redis
from redis.connection import ConnectionPool
import json
import os
from typing import Any, Optional, Union
import logging

logger = logging.getLogger(__name__)

class RedisManager:
    """Менеджер подключений к Redis"""
    
    def __init__(self, db: int = 0):
        self.host = os.getenv("REDIS_HOST", "localhost")
        self.port = int(os.getenv("REDIS_PORT", "6379"))
        self.db = db
        self.password = os.getenv("REDIS_PASSWORD")
        
        # Создание пула подключений
        self.pool = ConnectionPool(
            host=self.host,
            port=self.port,
            db=self.db,
            password=self.password,
            decode_responses=True,
            max_connections=20
        )
        
        # Создание клиента
        self.client = redis.Redis(connection_pool=self.pool)
        
        # Проверка подключения
        try:
            self.client.ping()
            logger.info(f"Redis connected: {self.host}:{self.port} DB={self.db}")
        except redis.ConnectionError as e:
            logger.error(f"Redis connection failed: {e}")
            raise
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Сохранение значения в Redis"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            result = self.client.set(key, value, ex=ttl)
            return result
        except Exception as e:
            logger.error(f"Redis SET error: {e}")
            return False
    
    def get(self, key: str, parse_json: bool = False) -> Optional[Any]:
        """Получение значения из Redis"""
        try:
            value = self.client.get(key)
            if value is None:
                return None
            
            if parse_json:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            
            return value
        except Exception as e:
            logger.error(f"Redis GET error: {e}")
            return None
    
    def delete(self, *keys: str) -> int:
        """Удаление ключей из Redis"""
        try:
            return self.client.delete(*keys)
        except Exception as e:
            logger.error(f"Redis DELETE error: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """Проверка существования ключа"""
        try:
            return self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis EXISTS error: {e}")
            return False
    
    def incr(self, key: str, amount: int = 1) -> Optional[int]:
        """Увеличение счетчика"""
        try:
            return self.client.incr(key, amount)
        except Exception as e:
            logger.error(f"Redis INCR error: {e}")
            return None
    
    def expire(self, key: str, ttl: int) -> bool:
        """Установка TTL для ключа"""
        try:
            return self.client.expire(key, ttl)
        except Exception as e:
            logger.error(f"Redis EXPIRE error: {e}")
            return False
    
    def hset(self, name: str, mapping: dict) -> int:
        """Сохранение hash"""
        try:
            return self.client.hset(name, mapping=mapping)
        except Exception as e:
            logger.error(f"Redis HSET error: {e}")
            return 0
    
    def hget(self, name: str, key: str) -> Optional[str]:
        """Получение значения из hash"""
        try:
            return self.client.hget(name, key)
        except Exception as e:
            logger.error(f"Redis HGET error: {e}")
            return None
    
    def hgetall(self, name: str) -> dict:
        """Получение всех значений hash"""
        try:
            return self.client.hgetall(name)
        except Exception as e:
            logger.error(f"Redis HGETALL error: {e}")
            return {}

# Предустановленные менеджеры для разных целей
class RedisInstances:
    """Предустановленные экземпляры Redis для разных целей"""
    
    # DB 0 - общие данные
    _general = None
    
    # DB 1 - JWT blacklist
    _jwt_blacklist = None
    
    # DB 2 - rate limiting
    _rate_limit = None
    
    # DB 3 - кэш данных
    _cache = None
    
    @classmethod
    def general(cls) -> RedisManager:
        """Общие данные (DB 0)"""
        if cls._general is None:
            cls._general = RedisManager(db=0)
        return cls._general
    
    @classmethod
    def jwt_blacklist(cls) -> RedisManager:
        """JWT blacklist (DB 1)"""
        if cls._jwt_blacklist is None:
            cls._jwt_blacklist = RedisManager(db=1)
        return cls._jwt_blacklist
    
    @classmethod
    def rate_limit(cls) -> RedisManager:
        """Rate limiting (DB 2)"""
        if cls._rate_limit is None:
            cls._rate_limit = RedisManager(db=2)
        return cls._rate_limit
    
    @classmethod
    def cache(cls) -> RedisManager:
        """Кэш данных (DB 3)"""
        if cls._cache is None:
            cls._cache = RedisManager(db=3)
        return cls._cache

# Convenience функции
def get_redis_client(db: int = 0) -> RedisManager:
    """Получение Redis клиента для конкретной БД"""
    return RedisManager(db=db)

# Функция для FastAPI dependency injection
def get_redis_general():
    """Dependency для общего Redis"""
    return RedisInstances.general()

def get_redis_cache():
    """Dependency для кэш Redis"""
    return RedisInstances.cache()
