from http import HTTPStatus
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from fastapi_cache.decorator import cache
from starlette import status

from core.pagination import PaginationParams
from models.film import FilmDetail, FilmListOutput
from models.genre import GenreUUID
from models.person import PersonUUID
from services.film import FilmService, get_film_service

router = APIRouter()


@router.get(
    '/{film_id}',
    response_model=FilmDetail,
    summary="Retrieve detailed information about a film")
@cache(expire=60)
async def film_details(
        film_id: str = Path(..., description="The ID of the film"),
        film_service: FilmService = Depends(get_film_service)
) -> FilmDetail:
    film = await film_service.get_film_from_elastic(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')
    return FilmDetail(
        uuid=film.get('id'),
        title=film.get('title'),
        imdb_rating=film.get('imdb_rating'),
        description=film.get('description'),
        genres=[
            GenreUUID(uuid=genre.get('id'),
                      name=genre.get('name')) for genre in film.get('genres')
        ],
        actors=[
            PersonUUID(uuid=actor.get('id'),
                       full_name=actor.get('name')) for actor in film.get('actors')
        ],
        writers=[
            PersonUUID(uuid=writer.get('id'),
                       full_name=writer.get('name')) for writer in film.get('writers')
        ],
        directors=[
            PersonUUID(uuid=director.get('id'),
                       full_name=director.get('name')) for director in film.get('directors')
        ]
    )


@router.get(
    '/',
    response_model=List[FilmListOutput],
    summary="Retrieve a list of films with optional search, filter by genre, and sorting options"
)
@cache(expire=60)
async def list_films_imbd_sorted(
        query: Optional[str] = Query(None, description="Search query for film titles"),
        sort: str = Query("-", description="Sort order ('+' for ascending, '-' for descending)"),
        genre: Optional[str] = Query(None, description="Filter by genre ID"),
        film_service: FilmService = Depends(get_film_service),
        pagination: PaginationParams = Depends(PaginationParams),
) -> List[FilmListOutput]:
    films = await film_service.get_films_list_filtered_searched_sorted(
        query=query,
        sort=sort,
        page_size=pagination.page_size,
        page_number=pagination.page,
        genre_id=genre)

    if not films:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No films found")

    return [FilmListOutput(uuid=film.uuid, title=film.title, imdb_rating=film.imdb_rating) for film in films]


@router.get(
    '/{film_id}/similar',
    response_model=List[FilmListOutput],
    summary="Get films similar to a specified film")
@cache(expire=60)
async def list_films_imbd_sorted(
        film_id: str = Path(..., description="The ID of the film for which to find similar films"),
        pagination: PaginationParams = Depends(PaginationParams),
        film_service: FilmService = Depends(get_film_service)
) -> List[FilmListOutput]:
    films = await film_service.get_similar_films(
        film_id=film_id,
        page_size=pagination.page_size,
        page_number=pagination.page
    )

    if not films:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No films found")

    return [FilmListOutput(uuid=film.uuid, title=film.title, imdb_rating=film.imdb_rating) for film in films]
