from fastapi import HTTPException
from model.person import Person
from model.credit import Credit
from service.dto.credit import CreaditUpdate, CreditCreate
from config.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from model.movie import Movie
from fastapi import Depends
from sqlalchemy.exc import IntegrityError

class CreditService:
  
  def __init__(self, db: AsyncSession) -> None:
    self.db = db
    
  async def create_credit(self, dto: CreditCreate) -> Credit:
    movie = (await self.db.execute(select(Movie).where(Movie.id == dto.movie_id))).scalars().first() # type: ignore
    if not movie:
      raise HTTPException(status_code=404, detail="Movie is not found")
    person = (await self.db.execute(select(Person).where(Person.id == dto.person_id))).scalars().first() # type: ignore
    if not person:
      raise HTTPException(status_code=404, detail="Person is not found")
    credit = Credit(**dto.model_dump())
    credit.movie = movie
    credit.person = person
    
    try:
      await self.db.commit()
      await self.db.refresh(credit)
    except IntegrityError:
      await self.db.rollback()
      raise
    return credit
  
  async def get_credit(self, id: int) -> Credit:
    credit = (await self.db.execute(select(Credit).where(Credit.id == id))).scalars().first() # type: ignore
    if credit is None:
      raise HTTPException(status_code=404, detail="Credit is not found")
    return credit
  
  async def update_credit(self, id: int, dto: CreaditUpdate) -> Credit:
    credit = (await self.db.execute(select(Credit).where(Credit.id == id))).scalars().first() # type: ignore
    if credit is None:
      raise HTTPException(status_code=404, detail="Credit is not found")
    movie = (await self.db.execute(select(Movie).where(Movie.id == dto.movie_id))).scalars().first() # type: ignore
    if not movie:
      raise HTTPException(status_code=404, detail="Movie is not found")
    person = (await self.db.execute(select(Person).where(Person.id == dto.person_id))).scalars().first() # type: ignore
    if not person:
      raise HTTPException(status_code=404, detail="Person is not found")
    map(
      lambda change: setattr(credit, change[0], change[1]), 
      filter(lambda item: item[1] is not None, dto.model_dump().items())
    )
    try:
      await self.db.commit()
      await self.db.refresh(credit)
    except IntegrityError:
      await self.db.rollback()
      raise
    return credit
  
  async def delete_credit(self, id: int) -> None:
    credit = (await self.db.execute(select(Credit).where(Credit.id == id))).scalars().first() # type: ignore
    if credit is None:
      raise HTTPException(status_code=404, detail="Credit is not found")
    await self.db.delete(credit)

def get_credit_service(db: AsyncSession = Depends(get_session)) -> CreditService:
  return CreditService(db)
