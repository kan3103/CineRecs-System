
import asyncio
from fastapi import HTTPException
from model.genre import Genre
from config.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from model.movie import Movie
from fastapi import Depends
from service.dto.movie import MovieCreate, MovieUpdate
from sqlalchemy.exc import IntegrityError

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
    
async def get_movie_service(db: AsyncSession = Depends(get_session)) -> MovieService:
  return MovieService(db)