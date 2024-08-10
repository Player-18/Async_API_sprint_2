from typing import Optional

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from db.elastic import get_elastic
from models.film import FilmListOutput
from models.person import PersonUUID, PersonWithFilms, FilmWithPersonRoles


class PersonService:
    """Service of person."""

    index = "persons"

    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def _get_films_with_person(
            self,
            person_id: str,
            page_size: int,
            page_number: int
    ) -> dict:
        """
        Query to ES for getting films with person.
        :return: Hits of ElasticSearch query.
        """
        query_films_with_person = {
            "size": page_size,
            "query": {
                "bool": {
                    "should": [
                        {
                            "nested": {
                                "path": "directors",
                                "query": {"bool": {"should": {"term": {"directors.id": f"{person_id}"}}}},
                            }
                        },
                        {
                            "nested": {
                                "path": "writers",
                                "query": {"bool": {"should": {"term": {"writers.id": f"{person_id}"}}}},
                            }
                        },
                        {
                            "nested": {
                                "path": "actors",
                                "query": {"bool": {"should": {"term": {"actors.id": f"{person_id}"}}}},
                            }
                        },
                    ]
                }
            },
            "from": (page_number - 1) * page_size  # Pagination
        }

        search_films_with_person = await self.elastic.search(body=query_films_with_person, index='movies')
        return search_films_with_person.body

    async def person_detail(
            self,
            person_id: str,
            page_size: int = 999,
            page_number: int = 1
    ) -> PersonWithFilms | None:
        """Detail of person with films and roles in those films."""

        response = await self.elastic.get(
            index=self.index, id=person_id
        )

        if not response["_source"]:
            return None

        search_films_with_person = await self._get_films_with_person(person_id, page_size, page_number)

        hits_films = search_films_with_person.get("hits", {}).get("hits", {})

        films_with_person_roles = []

        for film in hits_films:
            film_source = film["_source"]
            person_roles = []
            if film_source["actors"]:
                for actor in film_source["actors"]:
                    if actor["id"] == person_id:
                        person_roles.append('actor')
            if film_source["directors"]:
                for director in film_source["directors"]:
                    if director["id"] == person_id:
                        person_roles.append("director")

            if film_source["writers"]:
                for writer in film_source["writers"]:
                    if writer["id"] == person_id:
                        person_roles.append("writer")

            films_with_person_roles.append(FilmWithPersonRoles(uuid=film_source["id"], roles=person_roles))

        person = PersonWithFilms(uuid=response["_source"].get('id'), full_name=response["_source"].get('name'),
                                 films=films_with_person_roles)

        return person

    async def person_list(self, page_number: int, page_size: int) -> list[PersonUUID] | None:
        """Get list of person"""

        query = {
            "size": page_size,
            "query": {"match_all": {}},
            "from": (page_number - 1) * page_size,
        }

        response = await self.elastic.search(body=query, index=self.index)

        hits = response.get("hits")
        if not hits:
            return None
        persons = [PersonUUID(uuid=item["_source"].get('id'), full_name=item["_source"].get('name')) for item in
                   hits.get(
                       "hits")]
        return persons

    async def person_films(
            self,
            person_id,
            page_number: int = 1,
            page_size: int = 50
    ) -> list[FilmListOutput] | None:
        """
        Get films with person
        """
        search_films_with_person = await self._get_films_with_person(person_id, page_size, page_number)

        hits_films = search_films_with_person.get("hits", {}).get("hits", {})
        films = [FilmListOutput(uuid=film["_source"]['id'], title=film["_source"]['title'], imdb_rating=film["_source"][
            'imdb_rating']) for film in hits_films]
        return films

    async def person_search(self, page_number: int, page_size: int, query: Optional[str] = None) -> list[PersonWithFilms] | None:
        """Search for person"""

        # Query for searching persons by name.
        query = {
            "size": page_size,
            "query": {
                "bool": {
                    "should": {"match":
                                   {"name": query}
                               },
                }
            },
            "from": (page_number - 1) * page_size,
        }

        response = await self.elastic.search(body=query, index="persons")
        hits = response.get("hits")

        if not hits:
            return None

        # Get ID of found persons.
        founded_persons_id_list = [item["_source"].get('id') for item in hits.get("hits")]

        # Get detail(full_name, films) for found persons ID's
        founded_persons_with_details = [await self.person_detail(person_id) for person_id in founded_persons_id_list]

        return founded_persons_with_details


def person_service(
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    """Dependency for person service"""

    return PersonService(elastic)
