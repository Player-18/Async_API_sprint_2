import pytest

from tests.functional.testdata.indices import person_index
from tests.functional.testdata.person_data import person_data
from tests.functional.utils.es_utils import create_bulk_query

index_name = 'persons'


@pytest.mark.asyncio
async def test_get_all_persons(es_remove_and_create_index, es_write_data, make_get_request):
    person_bulk_query = create_bulk_query(index_name=index_name, data=person_data)

    await es_remove_and_create_index(index_name=index_name, index_settings=person_index)
    await es_write_data(index_name=index_name, data=person_bulk_query)

    response = await make_get_request('/api/v1/persons')

    assert response.status == 200

    assert len(response.body) == len(person_bulk_query)
