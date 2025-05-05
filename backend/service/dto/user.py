from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
  name: str
  date_of_birth: date
  username: str
  password: str
  embedding: dict[str, float] = {}
  
class UserUpdate(BaseModel):
  name: Optional[str]
  date_of_birth: Optional[date]
  embedding: dict[str, float] = {}
  new_password: Optional[str]
  old_password: Optional[str]

class UserResponse(BaseModel):
  id: int
  name: str
  date_of_birth: date
  username: str
  embedding: dict[str, float] = {}
  created_at: date
  
  model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
  username: str
  password: str

class LoginResponse(BaseModel):
  id: int
  name: str
  username: str
  token: str
  
  model_config = ConfigDict(from_attributes=True)
