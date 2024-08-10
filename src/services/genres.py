from typing import Optional, List

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from models.film import FilmListInput
from models.genre import Genre


class GenreService:
    """Сервис жанров."""

    index_genres = "genres"
    index_movies = "movies"

    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def genre_detail(self, id: str) -> Genre | None:
        """Деталка жанра"""

        response = await self.elastic.get(
            index=self.index_genres, id=id
        )

        if not response["_source"]:
            return None

        genre = Genre(**response["_source"])

        return genre

    async def genre_list(self, page_number: int, page_size: int) -> list[Genre] | None:
        """Получение списка жанров."""

        query = {
            "size": page_size,
            "query": {"match_all": {}},
            "from": (page_number - 1) * page_size,
        }

        response = await self.elastic.search(body=query, index=self.index_genres)

        hits = response.get("hits")
        if not hits:
            return None

        genres = [Genre(**item["_source"]) for item in hits.get("hits")]
        return genres

    async def get_popular_films(
            self,
            genre_id: str,
            page_number: int = 1,
            page_size: int = 50
    ) -> Optional[List[FilmListInput]]:
        """Retrieve films sorted by IMDb rating based on genre ID."""

        # Build the query to filter by nested genre and sort by IMDb rating
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
                                            {"term": {"genres.id": genre_id}}  # Filter by genre ID
                                        ]
                                    }
                                }
                            }
                        }
                    ]
                }
            },
            "sort": [
                {"imdb_rating": {"order": "desc"}}  # Sort by IMDb rating in descending order
            ],
            "from": (page_number - 1) * page_size  # Pagination
        }

        response = await self.elastic.search(body=query_body, index=self.index_movies)

        hits = response.get("hits", {}).get("hits", [])
        if not hits:
            return None

        films = [FilmListInput(**item["_source"]) for item in hits]
        return films


def genre_service(
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    """Прослайка для внедрения зависимости сервиса жанров."""

    return GenreService(elastic)
