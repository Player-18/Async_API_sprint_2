from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from fastapi_cache.decorator import cache

from core.pagination import PaginationParams
from models.film import FilmListOutput
from models.genre import Genre
from services.genres import GenreService, genre_service

router = APIRouter()


@router.get(
    "/",
    response_model=list[Genre],
    response_model_by_alias=False,
    summary="Список жанров",
)
@cache(expire=60)
async def genres(
        genre_service: GenreService = Depends(genre_service),
        pagination: PaginationParams = Depends(PaginationParams),
) -> list[Genre]:
    genres_list = await genre_service.genre_list(
        pagination.page, pagination.page_size
    )
    return genres_list


@router.get(
    "/{genre_id}",
    response_model=Genre,
    response_model_by_alias=False,
    summary="Деталка жанра",
)
@cache(expire=60)
async def genres(
        genre_id: str,
        genre_service: GenreService = Depends(genre_service),
) -> Genre:
    genre = await genre_service.genre_detail(
        genre_id
    )
    return genre


@router.get(
    "/{genre_id}/popular",
    response_model=List[FilmListOutput],
    summary="Get popular films by genre"
)
@cache(expire=60)
async def genres(
        genre_id: str = Path(..., description="The ID of the genre for which to find films"),
        pagination: PaginationParams = Depends(PaginationParams),
        genre_service: GenreService = Depends(genre_service)
) -> List[FilmListOutput]:
    films = await genre_service.get_popular_films(
        genre_id=genre_id,
        page_number=pagination.page,
        page_size=pagination.page_size
    )

    if not films:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No films found for this genre")

    return [FilmListOutput(uuid=film.uuid, title=film.title, imdb_rating=film.imdb_rating) for film in films]
