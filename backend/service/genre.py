
from fastapi import HTTPException
from model.genre import Genre
from service.dto.genre import GenreCreate, GenreUpdate
from config.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from model.movie import Movie
from fastapi import Depends
from sqlalchemy.exc import IntegrityError

class GenreService:
  
  def __init__(self, db: AsyncSession) -> None:
    self.db = db
    
  async def create_genre(self, dto: GenreCreate) -> Genre:
    genre = Genre(**dto.model_dump())
    self.db.add(genre)
    try:
      await self.db.commit()
      await self.db.refresh(genre)
    except IntegrityError:
      await self.db.rollback()
      raise
    return genre
  
  async def update_genre(self, id: int, dto: GenreUpdate) -> Genre:
    genre = (await self.db.execute(select(Genre).where(Genre.id == id))).scalars().first() # type: ignore
    if not genre:
      raise HTTPException(status_code=404, detail="Genre is not found")
    map(
      lambda change: setattr(genre, change[0], change[1]), 
      filter(lambda item: item[1] is not None, dto.model_dump().items())
    )
    try:
      await self.db.commit()
      await self.db.refresh(genre)
    except IntegrityError:
      await self.db.rollback()
      raise
    return genre
  
  async def get_genre(self, id: int) -> Genre:
    genre = (await self.db.execute(select(Genre).where(Genre.id == id))).scalars().first() # type: ignore
    if not genre:
      raise HTTPException(status_code=404, detail="Genre is not found")
    return genre
  
  async def delete_genre(self, id: int) -> None:
    genre = (await self.db.execute(select(Genre).where(Genre.id == id))).scalars().first() # type: ignore
    if not genre:
      raise HTTPException(status_code=404, detail="Genre is not found")
    await self.db.delete(genre)
    await self.db.commit()
    

async def get_genre_service(db: AsyncSession = Depends(get_session)) -> GenreService:
  return GenreService(db)