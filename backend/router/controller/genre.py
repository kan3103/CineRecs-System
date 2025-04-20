

from fastapi import APIRouter, Depends, HTTPException

from backend.service.genre import GenreService, get_genre_service
from service.dto.genre import GenreCreate, GenreResponse, GenreUpdate


router = APIRouter(tags=["genres"], prefix="/genres")

@router.post('/', response_model=GenreResponse, status_code=201)
async def create_genre(dto: GenreCreate, genre_service: GenreService = Depends(get_genre_service)) -> GenreResponse:
  try:
    genre = await genre_service.create_genre(dto)
    return GenreResponse.model_validate(genre)
  except HTTPException as e:
    raise e

@router.get('/{id}', response_model=GenreResponse, status_code=200)
async def get_genre(id: int, genre_service: GenreService = Depends(get_genre_service)) -> GenreResponse:
  try:
    genre = genre_service.get_genre(id)
    return GenreResponse.model_validate(genre)
  except HTTPException as e:
    raise e

@router.put('/{id}', response_model=GenreResponse, status_code=200)
async def update_genre(id: int, dto: GenreUpdate, genre_service: GenreService = Depends(get_genre_service)) -> GenreResponse:
  try:
    genre = genre_service.update_genre(id, dto)
    return GenreResponse.model_validate(genre)
  except HTTPException as e:
    raise e

@router.delete('/{id}', response_model=None, status_code=204)
async def delete_genre(id: int, genre_service: GenreService = Depends(get_genre_service)) -> None:
  try:
    await genre_service.delete_genre(id)
  except HTTPException as e:
    raise e