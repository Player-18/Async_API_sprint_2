from typing import Optional

from elasticsearch import AsyncElasticsearch

from core.config import config


es: Optional[AsyncElasticsearch] = None


# Функция понадобится при внедрении зависимостей
async def get_elastic() -> AsyncElasticsearch:
    return AsyncElasticsearch(hosts=[f'{config.es_url()}'])
