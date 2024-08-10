from pydantic import BaseModel, Field


class Genre(BaseModel):
    """Модель жанра."""

    uuid: str = Field(..., alias="id")
    name: str


class GenreUUID(BaseModel):
    """Модель жанра, принимающая поле UUID."""

    uuid: str
    name: str
