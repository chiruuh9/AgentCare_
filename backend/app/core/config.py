import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "AgentCare"
    API_V1_STR: str = "/api/v1"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./agentcare.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "secret")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        case_sensitive = True

settings = Settings()
