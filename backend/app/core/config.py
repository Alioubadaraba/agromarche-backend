from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "AgroMarché"
    DATABASE_URL: str = "postgresql://user:password@localhost/agromarche"
    SECRET_KEY: str = "changez-cette-cle-en-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    OPENWEATHER_API_KEY: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
