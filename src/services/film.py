from typing import Optional, List

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from models.film import FilmDetail, FilmListInput


class FilmService:
    """Film Service."""

    index = "movies"

    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def _search_films(self, query_body: dict) -> List[FilmListInput]:
        """Perform the search and return a list of FilmIMBDSortedInput."""
        response = await self.elastic.search(body=query_body, index=self.index)
        hits = response.get("hits", {}).get("hits", [])
        if not hits:
            return []
        return [FilmListInput(**item["_source"]) for item in hits]

    async def get_film_from_elastic(self, film_id: str) -> Optional[FilmDetail]:
        """Retrieve a single film from Elasticsearch."""
        try:
            doc = await self.elastic.get(index=self.index, id=film_id)
            return doc['_source']
        except NotFoundError:
            return None

    async def get_films_list_filtered_searched_sorted(
            self,
            query: Optional[str] = None,
            genre_id: Optional[str] = None,
            sort: Optional[str] = None,
            page_number: int = 1,
            page_size: int = 50
    ) -> List[FilmListInput] | None:
        """Retrieve a list of films with optional sorting, genre filtering, and full-text search."""

        sort_dict = {"+": "asc", "-": "desc"}

        # Construct filter conditions
        filter_conditions = []
        if genre_id:
            filter_conditions.append({
                "nested": {
                    "path": "genres",
                    "query": {
                        "bool": {
                            "must": [
                                {"term": {"genres.id": genre_id}}
                            ]
                        }
                    }
                }
            })

        # Construct search conditions
        search_conditions = []
        if query:
            search_conditions.append({"match": {"title": query}})

        # Build the query
        query_body = {
            "size": page_size,
            "query": {
                "bool": {
                    "must": search_conditions,
                    "filter": filter_conditions
                }
            },
            "from": (page_number - 1) * page_size,
        }

        # Add sorting if provided
        if sort != '-':
            sort_field = sort[1:] if sort.startswith(('+', '-')) else "imdb_rating"
            sort_order = sort_dict.get(sort[0], "desc") if sort.startswith(('+', '-')) else "desc"
            query_body["sort"] = [{sort_field: {"order": sort_order}}]

        return await self._search_films(query_body)

    async def get_similar_films(
            self,
            film_id: str,
            page_number: int = 1,
            page_size: int = 50
    ) -> List[FilmListInput]:
        """Retrieve similar films based on genre."""

        # Retrieve the film details from Elasticsearch
        film = await self.get_film_from_elastic(film_id)
        if not film:
            return []

        # Extract genres from the retrieved film
        genres = [genre["id"] for genre in film.get("genres", [])]

        # Build the query to find similar films based on the extracted genres
        query_body = {
            "size": page_size,
            "query": {
                "bool": {
                    "must": [
                        {
                            "nested": {
                                "path": "genres",
                                "query": {
                                    "bool": {
                                        "must": [
                                            {"terms": {"genres.id": genres}}  # Match any of the genres
                                        ]
                                    }
                                }
                            }
                        }
                    ],
                    "must_not": [
                        {"term": {"id": film_id}}  # Exclude the original film
                    ]
                }
            },
            "from": (page_number - 1) * page_size  # Pagination
        }

        return await self._search_films(query_body)


def get_film_service(
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    """Returns an instance of `FilmService` initialized with the provided Elasticsearch client."""
    return FilmService(elastic)
