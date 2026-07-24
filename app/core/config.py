from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str 
    JWT_SECRET: str
    REDIS_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    TEST_DATABASE_URL: str
    class Config:
        env_file = ".env"

settings = Settings()