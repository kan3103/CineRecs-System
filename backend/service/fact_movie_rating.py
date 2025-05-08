from fastapi import HTTPException
import time

from model.movie import Movie
from model.user import User
from model.fact_movie_rating import FactMovieRating
from service.dto.fact_movie_rating import FactMovieRatingCreate, FactMovieRatingUpdate
from config.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from fastapi import Depends
from sqlalchemy.exc import IntegrityError

class FactMovieRatingService:
  
  def __init__(self, db: AsyncSession) -> None:
    self.db = db
  
  async def create_fact_movie_rating(self, dto: FactMovieRatingCreate) -> FactMovieRating:
    user = (await self.db.execute(select(User).where(User.id == dto.user_id))).scalars().first() # type: ignore
    if user is None:
      raise HTTPException(status_code=404, detail="User is not found")
    movie = (await self.db.execute(select(Movie).where(Movie.id == dto.movie_id))).scalars().first() # type: ignore
    if movie is None:
      raise HTTPException(status_code=404, detail="Movie is not found")
      
    # Ensure we have an integer timestamp
    data = dto.model_dump()
    if 'timestamp' not in data or data['timestamp'] is None:
      data['timestamp'] = int(time.time())
      
    rating = FactMovieRating(**data)
    rating.user = user
    rating.movie = movie
    self.db.add(rating)
    try:
      await self.db.commit()
      await self.db.refresh(rating)
    except:
      await self.db.rollback()
      raise
    return rating
  
  async def update_fact_movie_rating(self, id: int, dto: FactMovieRatingUpdate) -> FactMovieRating:
    rating = (await self.db.execute(select(FactMovieRating).where(FactMovieRating.id == id))).scalars().first() # type: ignore
    if rating is None:
      raise HTTPException(status_code=404, detail="Fact movie rating is not found")
    map(
      lambda change: setattr(rating, change[0], change[1]), 
      filter(lambda item: item[1] is not None, dto.model_dump().items())
    )
    try:
      await self.db.commit()
      await self.db.refresh(rating)
    except IntegrityError:
      await self.db.rollback()
      raise
    return rating
  
  async def delete_fact_movie_rating(self, id: int) -> None:
    rating = (await self.db.execute(select(FactMovieRating).where(FactMovieRating.id == id))).scalars().first() # type: ignore
    if rating is None:
      raise HTTPException(status_code=404, detail="Fact movie rating is not found")
    await self.db.delete(rating)
    await self.db.commit()
    
  async def get_fact_movie_rating(self, id: int) -> FactMovieRating:
    rating = (await self.db.execute(select(FactMovieRating).where(FactMovieRating.id == id))).scalars().first() # type: ignore
    if rating is None:
      raise HTTPException(status_code=404, detail="Fact movie rating is not found")
    return rating
    
async def get_fact_movie_rating_service(db: AsyncSession = Depends(get_session)) -> FactMovieRatingService:
  return FactMovieRatingService(db)