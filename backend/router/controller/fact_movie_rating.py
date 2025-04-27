
from fastapi import APIRouter, Depends, HTTPException

from service.fact_movie_rating import FactMovieRatingService, get_fact_movie_rating_service
from service.dto.fact_movie_rating import FactMovieRatingCreate, FactMovieRatingResponse, FactMovieRatingUpdate


router = APIRouter(tags=["ratings"], prefix="/ratings")

@router.post('/', response_model=FactMovieRatingResponse, status_code=201)
async def create_fact_movie_rating(dto: FactMovieRatingCreate, fact_movie_rating_service: FactMovieRatingService = Depends(get_fact_movie_rating_service)) -> FactMovieRatingResponse:
  try:
    rating = await fact_movie_rating_service.create_fact_movie_rating(dto)
    return FactMovieRatingResponse.model_validate(rating)
  except HTTPException as e:
    raise e

@router.get('/{id}', response_model=FactMovieRatingResponse, status_code=200)
async def get_fact_movie_rating(id: int, fact_movie_rating_service: FactMovieRatingService = Depends(get_fact_movie_rating_service)) -> FactMovieRatingResponse:
  try:
    rating = await fact_movie_rating_service.get_fact_movie_rating(id)
    return FactMovieRatingResponse.model_validate(rating)
  except HTTPException as e:
    raise e

@router.put('/{id}', response_model=FactMovieRatingResponse, status_code=200)
async def update_fact_movie_rating(id: int, dto: FactMovieRatingUpdate, fact_movie_rating_service: FactMovieRatingService = Depends(get_fact_movie_rating_service)) -> FactMovieRatingResponse:
  try:
    rating = await fact_movie_rating_service.update_fact_movie_rating(id, dto)
    return FactMovieRatingResponse.model_validate(rating)
  except HTTPException as e:
    raise e

@router.delete('/{id}', response_model=None, status_code=204)
async def delete_fact_movie_rating(id: int, fact_movie_rating_service: FactMovieRatingService = Depends(get_fact_movie_rating_service)) -> None:
  try:
    await fact_movie_rating_service.delete_fact_movie_rating(id)
  except HTTPException as e:
    raise e