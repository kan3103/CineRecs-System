

from fastapi import APIRouter, Depends, HTTPException

from service.person import PersonService, get_person_service
from service.dto.person import PersonCreate, PersonResponse, PersonUpdate


router = APIRouter(tags=["people"], prefix="/people")

@router.post('/', response_model=PersonResponse, status_code=201)
async def create_person(dto: PersonCreate, person_service: PersonService = Depends(get_person_service)) -> PersonResponse:
  try:
    person = await person_service.create_person(dto)
    return PersonResponse.model_validate(person)
  except HTTPException as e:
    raise e

@router.put('/{id}', response_model=PersonResponse, status_code=200)
async def update_person(id: int, dto: PersonUpdate, person_service: PersonService = Depends(get_person_service)) -> PersonResponse:
  try:
    person = await person_service.update_person(id, dto)
    return PersonResponse.model_validate(person)
  except HTTPException as e:
    raise e

@router.get('/{id}', response_model=PersonResponse, status_code=200)
async def get_person(id: int, person_service: PersonService = Depends(get_person_service)) -> PersonResponse:
  try:
    person = await person_service.get_person(id)
    return PersonResponse.model_validate(person)
  except HTTPException as e:
    raise e

@router.delete('/{id}', response_model=PersonResponse, status_code=204)
async def delete_person(id: int, person_service: PersonService = Depends(get_person_service)) -> PersonResponse:
  try:
    await person_service.delete_person(id)
  except HTTPException as e:
    raise e