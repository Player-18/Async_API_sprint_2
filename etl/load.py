from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from backoff import backoff


@backoff(limit_of_retries=10)
def load_data_to_elastic_search(elasticsearch_host: str, data: list):
    """
    Function for loading data to Elasticsearch.
    :param elasticsearch_host: Host of elasticsearch.
    :param data: List with prepared data for inserting to the Elasticsearch
    :return: Result of loading to ES.
    """
    client = Elasticsearch(hosts=elasticsearch_host)
    result = bulk(client, data)
    return result

