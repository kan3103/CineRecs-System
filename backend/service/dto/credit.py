from typing import Optional
from pydantic import BaseModel, ConfigDict


class CreditCreate(BaseModel):
  movie_id: int
  person_id: int
  role: str
  job: str

class CreaditUpdate(BaseModel):
  role: Optional[str]
  job: Optional[str]

class CreditResponse(BaseModel):
  movie_id: int
  person_id: int
  role: str
  job: str
  
  model_config = ConfigDict(from_attributes=True)