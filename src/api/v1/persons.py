from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from fastapi_cache.decorator import cache
from starlette import status

from core.pagination import PaginationParams
from models.film import FilmListOutput
from models.person import PersonUUID, PersonWithFilms
from services.persons import PersonService, person_service

router = APIRouter()


@router.get(
    "/search",
    response_model=List[PersonWithFilms],
    summary="Search for person, return person detail with films and roles in those films.",
)
@cache(expire=60)
async def person_search(
        query: str = Query('', description="Search query for person name"),
        pagination: PaginationParams = Depends(PaginationParams),
        person_service: PersonService = Depends(person_service),
) -> list[PersonWithFilms]:
    found_persons = await person_service.person_search(
        query=query,
        page_size=pagination.page_size,
        page_number=pagination.page
    )

    if not found_persons:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Person not found.")

    return found_persons


@router.get(
    "/",
    response_model=list[PersonUUID],
    summary="List of all persons.",
)
@cache(expire=60)
async def person(
        pagination: PaginationParams = Depends(PaginationParams),
        person_service: PersonService = Depends(person_service)
) -> list[PersonUUID]:
    person_list = await person_service.person_list(
        page_size=pagination.page_size,
        page_number=pagination.page
    )

    if not person_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"There is no persons.")

    return person_list


@router.get(
    "/{person_id}",
    response_model=PersonWithFilms,
    summary="Person detail with films and roles in those films.",
)
@cache(expire=60)
async def persons(
        person_id: str = Path(..., description="The ID of person to find films with this person."),
        pagination: PaginationParams = Depends(PaginationParams),
        person_service: PersonService = Depends(person_service)
) -> PersonUUID:
    person = await person_service.person_detail(
        person_id=person_id,
        page_size=pagination.page_size,
        page_number=pagination.page
    )

    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No person with ID: {person_id}")

    return person


@router.get(
    "/{person_id}/film",
    response_model=List[FilmListOutput],
    summary="Films with person.",
)
@cache(expire=60)
async def films_with_person(
        person_id: str,
        pagination: PaginationParams = Depends(PaginationParams),
        person_service: PersonService = Depends(person_service),
) -> list[FilmListOutput] | None:
    films = await person_service.person_films(
        person_id=person_id,
        page_number=pagination.page,
        page_size=pagination.page_size
    )
    if not films:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No films found with this person")

    return films



