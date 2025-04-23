# app/core/config.py
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


# 환경 변수 설정
class Settings(BaseSettings):
    DB_ECHO_LOG: bool = False
    ASYNC_DATABASE_URL: str
    SYNC_DATABASE_URL: str

    model_config = ConfigDict(env_file=".env", extra="allow")


settings = Settings()
