from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from service.dto.movie import MovieCreate, MovieQuery, MovieResponse, MovieUpdate
from service.movie import MovieService, get_movie_service

router = APIRouter(tags=["movies"], prefix="/movies")

@router.get('/{id}', status_code=200, response_model=MovieResponse)
async def get_movie(id: int, movie_service: MovieService = Depends(get_movie_service)) -> MovieResponse:
  try:
    movie = await movie_service.get_movie(id)
    return MovieResponse.model_validate(movie)
  except HTTPException as e:
    raise e

@router.get('/', status_code=200)
async def get_movies_by_ids(ids: str, movie_service: MovieService = Depends(get_movie_service)):
    """
    Get multiple movies by their IDs
    Accepts a comma-separated list of movie IDs
    """
    try:
        # Parse the comma-separated movie IDs
        movie_ids = [int(id) for id in ids.split(',') if id.strip()]
        
        if not movie_ids:
            return []
            
        # Fetch each movie by ID
        movies = []
        for movie_id in movie_ids:
            try:
                movie = await movie_service.get_movie(movie_id)
                movies.append(MovieResponse.model_validate(movie))
            except HTTPException:
                # Skip movies that don't exist
                continue
                
        return movies
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid movie IDs: {str(e)}")

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

@router.post('/batch', status_code=200)
async def get_movies_batch(ids: list[int], movie_service: MovieService = Depends(get_movie_service)):
    """
    Get multiple movies by their IDs in a batch request
    Accepts a list of movie IDs in request body
    """
    try:
        # Use the new method that directly executes the SQL query with genre aggregation
        movies = await movie_service.get_movies_with_details(ids)
        return movies
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching movies: {str(e)}")

@router.post('/q', status_code=200, response_model=Dict[str, Any])
async def get_movies(dto: MovieQuery, page: int = 1, limit: int = 25, movie_service: MovieService = Depends(get_movie_service)) -> Dict[str, Any]:
  try:
    movies, total_items, total_pages = await movie_service.get_movies(dto, page, limit)
  
    return {
      "items": list(map(lambda e: MovieResponse.model_validate(e), movies)), 
      "total_items": total_items, 
      "total_pages": total_pages
    }
  except HTTPException as e:
    raise e