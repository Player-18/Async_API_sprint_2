from typing import List

from pydantic import BaseModel


class Person(BaseModel):
    """Модель персоны."""

    id: str
    full_name: str


class PersonUUID(BaseModel):
    """Модель персоны c UUID."""

    uuid: str
    full_name: str


class FilmWithPersonRoles(BaseModel):
    """Модель списка фильмов."""

    uuid: str
    roles: List[str]


class PersonWithFilms(PersonUUID):
    """Модель персоны c UUID."""

    films: List[FilmWithPersonRoles]