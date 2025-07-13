from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/scheduler"
    
    # Hasura
    hasura_graphql_endpoint: str = "http://localhost:8080/v1/graphql"
    hasura_admin_secret: str = "myadminsecretkey"
    
    # JWT
    jwt_secret_key: str = "mysecretjwtkey12345678901234567890"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # CORS
    cors_origins: List[str] = ["http://localhost:4200"]
    
    # Environment
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
