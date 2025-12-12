from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    APP_NAME: str = "Wedding Backend"

    MONGO_URI: str = Field(default="mongodb://mongo:27017")
    MASTER_DB: str = Field(default="master_db")

    SECRET_KEY: str = Field(default="add key here")  # will be overridden by .env
    TOKEN_EXPIRE_HOURS: int = 6

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
