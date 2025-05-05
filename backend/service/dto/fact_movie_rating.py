
import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

class FactMovieRatingCreate(BaseModel):
  user_id: int
  movie_id: int
  rating: float

class FactMovieRatingUpdate(BaseModel):
  rating: Optional[float]
  
class FactMovieRatingResponse(BaseModel):
  user_id: int
  movie_id: int
  rating: float
  timestamp: int
  date: datetime.date
  
  model_config = ConfigDict(from_attributes=True)