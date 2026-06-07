try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./drivelegal.db"
    openai_api_key: str = ""
    gemini_api_key: str = ""
    chroma_host: str = "localhost"
    chroma_port: int = 8001
    chroma_collection: str = "traffic_laws"
    jwt_secret: str = "change-me-in-production"
    frontend_url: str = "http://localhost:5173"

    class Config:
        env_file = ".env"

settings = Settings()
