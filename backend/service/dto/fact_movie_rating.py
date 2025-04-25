
from pydantic import BaseModel, ConfigDict
from typing import Optional

class FactMovieRatingCreate(BaseModel):
  user_id: int
  movie_id: int
  rating: float

class FactMovingRatingUpdate(BaseModel):
  rating: Optional[float]
  
class FactMovieRatingResponse(BaseModel):
  id: int
  user_id: int
  movie_id: int
  rating: float
  
  model_config = ConfigDict(from_attributes=True)