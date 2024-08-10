import os
from logging import config as logging_config

from pydantic import BaseSettings, Field

from core.logger import LOGGING


class Settings(BaseSettings):
    # Корень проекта
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Название проекта. Используется в Swagger-документации
    project_name: str = Field(env="PROJECT_NAME", default="movies")

    elastic_host: str = Field(env="ES_HOST", default="127.0.0.1")
    elastic_port: int = Field(env="ES_PORT", default=9200)
    elastic_schema = os.getenv("ES_SCHEMA", "http://")

    redis_host: str = Field(env="REDIS_HOST", default="127.0.0.1")
    redis_port: int = Field(env="REDIS_PORT", default=6379)

    def es_url(self):
        return f'{self.elastic_schema}{self.elastic_host}:{self.elastic_port}'


# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

config = Settings()
