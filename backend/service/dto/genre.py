

from typing import Optional
from pydantic import BaseModel, ConfigDict


class GenreCreate(BaseModel):
  type: str
  overall_rating: Optional[float]
  
class GenreUpdate(BaseModel):
  type: Optional[str]
  overall_rating: Optional[float]

class GenreResponse(BaseModel):
  id: int
  type: str
  overall_rating: Optional[float]
  
  model_config = ConfigDict(from_attributes=True)
  