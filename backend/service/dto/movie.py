
from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict



class MovieCreate(BaseModel):
  name: str
  rated: str
  total_rating: Optional[float]
  rating_total_count: Optional[int]
  runtime: str
  release_date: date
  budget: Optional[float]
  revenue: Optional[str]
  description: Optional[str]
  status: bool
  poster: Optional[str]
  country: str
  language: str
  genres: list[int] = []

class MovieUpdate(BaseModel):
  name: Optional[str]
  rated: Optional[str]
  total_rating: Optional[float]
  rating_total_count: Optional[int]
  runtime: Optional[str]
  release_date: Optional[date]
  budget: Optional[float]
  revenue: Optional[str]
  description: Optional[str]
  status: Optional[bool]
  poster: Optional[str]
  country: Optional[str]
  language: Optional[str]
  genres: Optional[list[int]]

class MovieResponse(BaseModel):
  id: int
  rated: str
  total_rating: Optional[float]
  rating_total_count: Optional[int]
  runtime: str
  release_date: date
  budget: Optional[float]
  revenue: Optional[str]
  description: Optional[str]
  status: bool
  poster: Optional[str]
  country: str
  language: str
  genres: list[str] = []
  
  model_config = ConfigDict(from_attributes=True)