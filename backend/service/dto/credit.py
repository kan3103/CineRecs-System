from typing import Optional
from pydantic import BaseModel, ConfigDict


class CreditCreate(BaseModel):
  movie_id: int
  person_id: int
  job: str

class CreaditUpdate(BaseModel):
  job: Optional[str]

class CreditResponse(BaseModel):
  id: int
  movie_id: int
  person_id: int
  job: str
  
  model_config = ConfigDict(from_attributes=True)