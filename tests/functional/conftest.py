import asyncio
from typing import List

import aiohttp
import pytest_asyncio
from elasticsearch.helpers import async_bulk
from elasticsearch import AsyncElasticsearch
from tests.functional.settings import test_settings
from tests.functional.testdata.models import Response


@pytest_asyncio.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(name='es_client', scope='session')
async def es_client():
    es_client = AsyncElasticsearch(hosts=test_settings.es_url(), verify_certs=False)
    yield es_client
    await es_client.close()


@pytest_asyncio.fixture(name='es_remove_and_create_index')
def es_remove_and_create_index(es_client):
    async def inner(index_name: str, index_settings: dict):
        """
        Fixture removes index with all data if it exists.
        Then create index without data.
        :param index_name:  The name of index.
        :param index_settings: Dictionary settings for creating index.
        """
        if await es_client.indices.exists(index=index_name):
            await es_client.indices.delete(index=index_name)
        await es_client.indices.create(index=index_name, **index_settings)
    return inner


@pytest_asyncio.fixture(name='es_write_data')
def es_write_data(es_client):
    async def inner(index_name: str, data: List[dict]):
        """
        Fixture adds prepared data to index.
        :param index_name: The name of index.
        :param data: Prepared data for writing to index.
        """
        updated, errors = await async_bulk(client=es_client, actions=data)

        # Add sleep to wait for loading data to ES.
        await asyncio.sleep(1)

        if errors:
            raise Exception(f'Error of data adding to {index_name} index of ES.')
    return inner


@pytest_asyncio.fixture
def make_get_request():
    async def inner(es_query: str, params: dict = None):

        url = f"{test_settings.api_url()}{es_query}"

        session = aiohttp.ClientSession()

        async with session.get(url, params=params) as response:
            return Response(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return inner


