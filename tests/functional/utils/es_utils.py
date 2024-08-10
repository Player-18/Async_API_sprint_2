from typing import List, Dict


def create_bulk_query(index_name: str, data: dict) -> List[Dict]:
    bulk = [{'_index': index_name, '_id': row['id'], '_source': row} for row in data]

    return bulk
