from functools import lru_cache
from typing import Any, Dict, Optional

from pydantic import PostgresDsn, field_validator
from pydantic_core.core_schema import FieldValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Services YooCard With Based Method"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    USERS_OPEN_REGISTRATION: str

    ENVIRONMENT: Optional[str]

    FIRST_SUPER_ADMIN_FIRST_NAME: str
    FIRST_SUPER_ADMIN_LAST_NAME: str
    FIRST_SUPER_ADMIN_USERNAME: str
    FIRST_SUPER_ADMIN_EMAIL: str
    FIRST_SUPER_ADMIN_PASSWORD: str

    SSH_HOST: Optional[str] = None
    SSH_PORT: Optional[int] = None
    SSH_USERNAME: Optional[str] = None
    SSH_PASSWORD: Optional[str] = None
    REMOTE_DB_HOST: Optional[str] = None
    REMOTE_DB_PORT: Optional[int] = None

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    DOMAIN: str

    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    ASYNC_SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @field_validator("SQLALCHEMY_DATABASE_URI")
    def assemble_db_connection(
        cls, v: Optional[str], values: FieldValidationInfo
    ) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            username=values.data.get("DB_USER"),
            password=values.data.get("DB_PASSWORD"),
            host=values.data.get("DB_HOST"),
            port=values.data.get("DB_PORT"),
            path=f"{values.data.get('DB_NAME') or ''}"
        )

    @field_validator("ASYNC_SQLALCHEMY_DATABASE_URI")
    def assemble_async_db_connection(
        cls, v: Optional[str], values: FieldValidationInfo
    ) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.data.get("DB_USER"),
            password=values.data.get("DB_PASSWORD"),
            host=values.data.get("DB_HOST"),
            port=values.data.get("DB_PORT"),
            path=f"{values.data.get('DB_NAME') or ''}"
        )

    def load_env_file(self, _env_file):
        self.__init__(_env_file=_env_file)

    class Config:
        case_sensitive = True
        env_file = ".env.development"


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
