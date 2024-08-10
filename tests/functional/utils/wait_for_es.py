import time

from tests.functional.settings import Settings
from elasticsearch import Elasticsearch

settings = Settings()


if __name__ == '__main__':
    es_client = Elasticsearch(hosts=settings.es_url())
    while True:
        if es_client.ping():
            break
        time.sleep(1)
