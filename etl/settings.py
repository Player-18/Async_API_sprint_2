from os.path import dirname, join
from typing import ClassVar

from pydantic import BaseSettings, Field
from redis import StrictRedis
from dotenv import load_dotenv

from state.etl_state import StateETL
from state.redis_state_storage import State, RedisStorage

dotenv_path = join(dirname(dirname(__file__)), 'src/.env')
load_dotenv(dotenv_path)


class DbSettings(BaseSettings):
    dbname: str = Field(env='POSTGRES_DB')
    user: str = Field(env='POSTGRES_USER')
    password: str = Field(env='POSTGRES_PASSWORD')
    host: str = Field(env='POSTGRES_HOST')
    port: int = Field(env='POSTGRES_PORT')
    options: str = Field(env='POSTGRES_OPTIONS')


class EsSettings(BaseSettings):
    host: str = Field(env='ES_HOST')
    port: str = Field(env='ES_PORT')

    def get_url(self):
        return f'http://{self.host}:{self.port}'


class RedisSettings(BaseSettings):
    redis_host: str = Field(env='REDIS_HOST')
    redis_port: str = Field(env='REDIS_PORT')


class BaseConfigs(BaseSettings):

    batch: int = Field(100, env='BATCH_SIZE')
    border_sleep_time: float = Field(10.0, env='BORDER_SLEEP_TIME')
    run_etl_every_seconds: int = Field(60, env='RUN_ETL_EVERY_SECONDS')
    es_url: str = EsSettings().get_url()
    redis_settings: dict = RedisSettings().dict()
    dsn: dict = DbSettings().dict()
    etl_state: ClassVar[StateETL] = StateETL(State(RedisStorage(StrictRedis(host=redis_settings['redis_host'],
                                                                            port=redis_settings['redis_port'],
                                                                            decode_responses=True))))
