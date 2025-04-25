from datetime import datetime
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException
from sqlalchemy.exc import IntegrityError
import bcrypt

from config.db import get_session
from model.user import User
from service.dto.user import UserCreate, UserUpdate

class UserService:
  
  def __init__(self, db: AsyncSession):
    self.db = db
  
  async def create_user(self, dto: UserCreate) -> User:
    user_existed = (await self.db.execute(select(User).where(User.username == dto.username))).scalars().first() # type: ignore
    if user_existed:
      raise HTTPException(status_code=409, detail="Username has already existed")
    
    user = User(name=dto.name, username=dto.username, password=bcrypt.hashpw(dto.password.encode(), bcrypt.gensalt()).decode(), 
                date_of_birth=dto.date_of_birth, embedding=dto.embedding, created_at=datetime.now())
    self.db.add(user)
    try:
      await self.db.commit()
      await self.db.refresh(user)
    except IntegrityError:
      await self.db.rollback()
      raise
    return user
  
  async def get_user(self, id: int) -> User:
    user = (await self.db.execute(select(User).where(User.id == id))).scalars().first() # type: ignore
    if not user:
      raise HTTPException(status_code=404, detail="User is not found")
    return user
  
  async def update_user(self, id: int, dto: UserUpdate) -> User:
    user = (await self.db.execute(select(User).where(User.id == id))).scalars().first() # type: ignore
    if not user:
      raise HTTPException(status_code=404, detail="User is not found")

    if dto.name:    
      user.name = dto.name
    if dto.date_of_birth:
      user.date_of_birth = dto.date_of_birth
    if dto.embedding:
      user.embedding = dto.embedding
    if dto.old_password and dto.new_password:
      if not bcrypt.checkpw(dto.old_password.encode(), user.password.encode()):
        raise HTTPException(status_code=403, detail="Password is incorrect")
      user.password = bcrypt.hashpw(dto.new_password.encode(), bcrypt.gensalt()).decode()
    
    try:
      await self.db.commit()
      await self.db.refresh(user)
    except IntegrityError:
      await self.db.rollback()
      raise HTTPException(status_code=409, detail="Username has already existed")
    return user
  
  async def delete_user(self, id: int) -> None:
    user = (await self.db.execute(select(User).where(User.id == id))).scalars().first() # type: ignore
    if not user:
      raise HTTPException(status_code=404, detail="User is not found")
    await self.db.delete(user)
    await self.db.commit()

async def get_user_service(db: AsyncSession = Depends(get_session)) -> UserService: 
  return UserService(db)
    