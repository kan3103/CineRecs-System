from datetime import datetime
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException
from sqlalchemy.exc import IntegrityError

from model.person import Person
from service.dto.person import PersonCreate, PersonUpdate, PersonResponse
from config.db import get_session

class PersonService:
  
  def __init__(self, db: AsyncSession) -> None:
    self.db = db
    
  async def create_person(self, dto: PersonCreate) -> Person:
    person = Person(**dto.model_dump())
    self.db.add(person)
    try:
      await self.db.commit()
      await self.db.refresh(person)
    except IntegrityError:
      await self.db.rollback()
      raise
    return person
  
  async def update_person(self, id: int, dto: PersonUpdate) -> Person:
    person = (await self.db.execute(select(Person).where(Person.id == id))).scalars().first() # type: ignore
    if not person:
      raise HTTPException(status_code=404, detail="Person is not found")
    map(
      lambda change: setattr(person, change[0], change[1]), 
      filter(lambda item: item[1] is not None, dto.model_dump().items())
    )
    try:
      await self.db.commit()
      await self.db.refresh(person)
    except IntegrityError:
      await self.db.rollback()
      raise
  
    return person
    
  async def delete_person(self, id: int) -> None:
    person = (await self.db.execute(select(Person).where(Person.id == id))).scalars().first() # type: ignore
    if not person:
      raise HTTPException(status_code=404, detail="Person is not found")
    await self.db.delete(person)
    await self.db.commit()
    
  async def get_person(self, id: int) -> Person:
    person = (await self.db.execute(select(Person).where(Person.id == id))).scalars().first() # type: ignore
    if not person:
      raise HTTPException(status_code=404, detail="Person is not found")
    return person
    
    
async def get_person_service(db: AsyncSession = Depends(get_session)) -> PersonService:
  return PersonService(db)