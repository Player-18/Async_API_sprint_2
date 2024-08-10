from typing import List, Optional
from pydantic import BaseModel


class Base(BaseModel):
    id: str


class Genre(Base):
    name: str


class GenreData(Genre):
    description: str = None


class PersonData(Base):
    name: str


class Person(PersonData):
    role: List[str] = []
    film_ids: List[str] = []


class Film(Base):
    title: str
    description: str = None
    imdb_rating: Optional[float] = None
    genres: List[Genre] | None = []
    actors: List[PersonData] | None = []
    directors: List[PersonData] | None = []
    writers: List[PersonData] | None = []
