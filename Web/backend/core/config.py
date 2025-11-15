from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./eidos.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # AI
    DEEPSEEK_API_KEY: str = "sk-f4d81c913e69482c8df77a9032817488"
    
    class Config:
        env_file = ".env"

settings = Settings()
