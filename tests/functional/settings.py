import os
from os.path import join, dirname

from dotenv import load_dotenv
from pydantic import BaseSettings, Field

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


class Settings(BaseSettings):
    # Название проекта. Используется в Swagger-документации
    project_name: str = Field(env="PROJECT_NAME", default="movies")

    elastic_schema = os.getenv("ES_SCHEMA", "http://")
    elastic_host: str = Field(env="ES_HOST", default="127.0.0.1")
    elastic_port: int = Field(env="ES_PORT", default=9200)

    api_schema = os.getenv("API_SCHEMA", "http://")
    api_host: str = Field(env="API_HOST", default="127.0.0.1")
    api_port: int = Field(env="API_PORT", default=8080)

    redis_host: str = Field(env="REDIS_HOST", default="127.0.0.1")
    redis_port: int = Field(env="REDIS_PORT", default=6379)

    def es_url(self):
        return f'{self.elastic_schema}{self.elastic_host}:{self.elastic_port}'

    def api_url(self):
        return f'{self.api_schema}{self.api_host}:{self.api_port}'


test_settings = Settings()

