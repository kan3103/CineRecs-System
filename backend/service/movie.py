import asyncio
import math
from fastapi import HTTPException
from model.genre import Genre
from config.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from model.movie import Movie
from fastapi import Depends
from service.dto.movie import MovieCreate, MovieQuery, MovieUpdate
from sqlalchemy.exc import IntegrityError
from sqlalchemy import true, func
from sqlalchemy.orm import selectinload
from sqlalchemy import text
class MovieService:
  
  def __init__(self, db: AsyncSession):
    self.db = db
  
  async def get_movie(self, id: int) -> Movie:
    movie = (await self.db.execute(select(Movie).where(Movie.id == id))).scalars().first() # type: ignore
    if not movie:
      raise HTTPException(status_code=404, detail="Movie is not found")
    return movie
  
  async def create_movie(self, dto: MovieCreate) -> Movie:
    movie = Movie(**dto.model_dump())
    
    async def get_genre(id: int) -> Genre:
      genre = (await self.db.execute(select(Genre).where(Genre.id == id))).scalars().first() # type: ignore
      if not genre:
        raise HTTPException(status_code=404, detail="Genre is not found")
      return genre
    genres: list[Genre] = await asyncio.gather(*list(map(get_genre, dto.genre_ids)))
    
    movie.genres.extend(genres) # type: ignore
    
    self.db.add(movie)
    try:
      await self.db.commit()
      await self.db.refresh(movie)
    except IntegrityError:
      await self.db.rollback()
      raise
    return movie
  
  async def update_movie(self, id: int, dto: MovieUpdate) -> Movie:
    movie = (await self.db.execute(select(Movie).where(Movie.id == id))).scalars().first() # type: ignore
    
    if not movie:
      raise HTTPException(status_code=404, detail="Movie is not found")
    for field, value in dto.model_dump().items():
      if value is not None and field not in ["id", "genres", "ratings", "credits"]:
        setattr(movie, field, value)
    try:
      await self.db.commit()
      await self.db.refresh(movie)
    except IntegrityError:
      await self.db.rollback()
      raise
    return movie
  
  async def delete_movie(self, id: int) -> None:
    movie = (await self.db.execute(select(Movie).where(Movie.id == id))).scalars().first() # type: ignore
    if not movie:
      raise HTTPException(status_code=404, detail="Movie is not found")
    await self.db.delete(movie)
    await self.db.commit()
    
  async def get_movies(self, dto: MovieQuery, page: int, limit: int) -> tuple[list[Movie], int, int]:
    
    count_query = (
      select(func.count()).where(Movie.rated.like(f"%{dto.rated}%") if dto.rated is not None else true())  # type: ignore
        .where(func.lower(Movie.name).like(f"%{dto.name.lower()}%") if dto.name is not None else true())  # type: ignore
        .where(Movie.total_rating >= dto.min_total_rating if dto.min_total_rating is not None else true())  # type: ignore
        .where(Movie.total_rating <= dto.max_total_rating if dto.max_total_rating is not None else true()) # type: ignore
        .where(Movie.runtime >= dto.min_runtime if dto.min_runtime is not None else true()) # type: ignore
        .where(Movie.runtime <= dto.max_runtime if dto.max_runtime is not None else true()) # type: ignore
        .where(Movie.release_date >= dto.from_release_date if dto.from_release_date is not None else true()) # type: ignore
        .where(Movie.release_date <= dto.to_release_date if dto.to_release_date is not None else true()) # type: ignore
        .where(Movie.revenue >= dto.min_revenue if dto.min_revenue is not None else true()) # type: ignore
        .where(Movie.revenue <= dto.max_revenue if dto.max_revenue is not None else true()) # type: ignore
        .where(func.lower(Movie.description).lower().like(f"%{dto.description.lower()}%") if dto.description is not None else true()) # type: ignore
        .where(Movie.status == dto.status if dto.status is not None else true()) # type: ignore
        .where(Movie.language.in_(dto.languages) if dto.languages is not None else true()) # type: ignore
        .where(Movie.countries.in_(dto.countries) if dto.countries is not None else true()) # type: ignore 
    )
    total_items = (await self.db.execute(count_query)).scalar_one()
    total_pages = math.ceil((float(total_items) / limit))
    page_num = min(page, total_pages)
    offset = (page_num - 1) * limit
    
    item_query = (
      select(Movie).where(Movie.rated.like(f"%{dto.rated}%") if dto.rated is not None else true())  # type: ignore
        .where(Movie.name.like(f"%{dto.name}%") if dto.name is not None else true())  # type: ignore
        .where(Movie.total_rating >= dto.min_total_rating if dto.min_total_rating is not None else true())  # type: ignore
        .where(Movie.total_rating <= dto.max_total_rating if dto.max_total_rating is not None else true()) # type: ignore
        .where(Movie.runtime >= dto.min_runtime if dto.min_runtime is not None else true()) # type: ignore
        .where(Movie.runtime <= dto.max_runtime if dto.max_runtime is not None else true()) # type: ignore
        .where(Movie.release_date >= dto.from_release_date if dto.from_release_date is not None else true()) # type: ignore
        .where(Movie.release_date <= dto.to_release_date if dto.to_release_date is not None else true()) # type: ignore
        .where(Movie.revenue >= dto.min_revenue if dto.min_revenue is not None else true()) # type: ignore
        .where(Movie.revenue <= dto.max_revenue if dto.max_revenue is not None else true()) # type: ignore
        .where(Movie.description.like(f"%{dto.description}%") if dto.description is not None else true()) # type: ignore
        .where(Movie.status == dto.status if dto.status is not None else true()) # type: ignore
        .where(Movie.language.in_(dto.languages) if dto.languages is not None else true()) # type: ignore
        .where(Movie.countries.in_(dto.countries) if dto.countries is not None else true()) # type: ignore 
        .options(selectinload(Movie.genres)) # type: ignore
    ).offset(offset).limit(limit)
    movies = list( (await self.db.execute(item_query)).scalars().all() )
    return movies, total_items, total_pages
    
  async def get_movies_with_details(self, movie_ids: list[int]) -> list[dict]:
    """
    Get details for multiple movies including accurate genre information
    using the raw SQL query with the genre_agg join
    """
    if not movie_ids:
      return []
      
    try:
      # Use ORM approach instead of raw SQL to avoid greenlet issues
      query = (
        select(Movie)
        .where(Movie.id.in_(movie_ids))
        .options(selectinload(Movie.genres))
      )
      
      result = await self.db.execute(query)
      movies = result.scalars().all()
      
      movies_list = []
      for movie in movies:
        # Format movie data for response
        genres_list = [genre.type for genre in movie.genres] if movie.genres else []
        
        movies_list.append({
          "id": movie.id,
          "title": movie.name,
          "release_date": str(movie.release_date) if movie.release_date else None,
          "poster_url": movie.poster,
          "genres": genres_list,
          "description": movie.description,
          "roles": []  # This would require a separate query for roles
        })
      
      # Add placeholders for movies not found
      found_ids = {movie.id for movie in movies}
      for movie_id in movie_ids:
        if movie_id not in found_ids:
          movies_list.append({
            "id": movie_id,
            "title": f"Movie {movie_id}",
            "release_date": None,
            "poster_url": None,
            "genres": [],
            "description": None,
            "roles": []
          })
      
      return movies_list
    except Exception as e:
      print(f"Error in get_movies_with_details: {str(e)}")
      raise HTTPException(status_code=500, detail=f"Error fetching movies: {str(e)}")
      
          
async def get_movie_service(db: AsyncSession = Depends(get_session)) -> MovieService:
  return MovieService(db)