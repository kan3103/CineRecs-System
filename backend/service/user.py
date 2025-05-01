from datetime import datetime, timedelta
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException
from sqlalchemy.exc import IntegrityError
import bcrypt
import jwt
from typing import Optional

from config.db import get_session
from model.user import User
from service.dto.user import UserCreate, UserUpdate, LoginResponse

# Secret key for JWT token generation
SECRET_KEY = "cinerecs_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

class UserService:
  
  def __init__(self, db: AsyncSession):
    self.db = db
  
  async def create_user(self, dto: UserCreate) -> User:
    user_existed = (await self.db.execute(select(User).where(User.username == dto.username))).scalars().first() # type: ignore
    if user_existed:
      raise HTTPException(status_code=409, detail="Username already exists")
    
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
    
  async def authenticate_user(self, username: str, password: str) -> LoginResponse:
    user = (await self.db.execute(select(User).where(User.username == username))).scalars().first() # type: ignore
    if not user:
      raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    if not bcrypt.checkpw(password.encode(), user.password.encode()):
      raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    # Create access token
    token_data = {
      "sub": str(user.id),
      "username": user.username,
      "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    return LoginResponse(
      id=user.id,
      name=user.name,
      username=user.username,
      token=token
    )
  
  async def username_exists(self, username: str) -> bool:
    user = (await self.db.execute(select(User).where(User.username == username))).scalars().first() # type: ignore
    return user is not None

async def get_user_service(db: AsyncSession = Depends(get_session)) -> UserService: 
  return UserService(db)
