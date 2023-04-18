from pydantic import BaseSettings
from sqlalchemy.ext.declarative import declarative_base


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    DB_URL: str = "postgresql+asyncpg://teste:12345@localhost:5432/faculdade"
    DBBaseModel = declarative_base()

    JWT_SECRET: str = "mAOovr8Rq2l98lx5d2QL00turDYnP5HWQnysCyG9eZM"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    class Config:
        case_sensitive = True


settings: Settings = Settings()
