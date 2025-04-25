

from fastapi import APIRouter, Depends, HTTPException

from service.dto.movie import MovieCreate, MovieResponse, MovieUpdate
from service.movie import MovieService, get_movie_service



router = APIRouter(tags=["movies"], prefix="/movies")

@router.get('/{id}', status_code=200, response_model=MovieResponse)
async def get_movie(id: int, movie_service: MovieService = Depends(get_movie_service)) -> MovieResponse:
  try:
    movie = await movie_service.get_movie(id)
    return MovieResponse.model_validate(movie)
  except HTTPException as e:
    raise e

@router.post('/', status_code=201, response_model=MovieResponse)
async def create_movie(dto: MovieCreate, movie_service: MovieService = Depends(get_movie_service)) -> MovieResponse:
  try:
    movie = await movie_service.create_movie(dto)
    return MovieResponse.model_validate(movie)
  except HTTPException as e:
    raise e

@router.put('/{id}', status_code=200, response_model=MovieResponse)
async def update_movie(id: int, dto: MovieUpdate, movie_service: MovieService = Depends(get_movie_service)) -> MovieResponse:
  try:
    movie = await movie_service.update_movie(id, dto)
    return MovieResponse.model_validate(movie)
  except HTTPException as e:
    raise e

@router.delete('/{id}', status_code=204, response_model=None)
async def delete_movie(id: int, movie_service: MovieService = Depends(get_movie_service)) -> None:
  try:
    await movie_service.delete_movie(id)
  except HTTPException as e:
    raise e