from contextlib import asynccontextmanager

import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis.asyncio import Redis

from api.v1 import films, genres, persons
from core.config import config
from db import redis, elastic


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize Redis and Elasticsearch
    redis.redis = Redis(host=config.redis_host, port=config.redis_port)
    await redis.redis.ping()  # Ensure Redis is ready
    FastAPICache.init(RedisBackend(redis.redis), prefix="fastapi-cache")
    elastic.es = AsyncElasticsearch(hosts=[config.es_url()])

    yield

    # Shutdown: close Redis and Elasticsearch connections
    await redis.redis.close()
    await elastic.es.close()


app = FastAPI(
    title=config.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(films.router, prefix='/api/v1/films', tags=['films'])
app.include_router(genres.router, prefix='/api/v1/genres', tags=['genres'])
app.include_router(persons.router, prefix='/api/v1/persons', tags=['persons'])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
