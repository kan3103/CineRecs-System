
from datetime import date
from typing import Optional
from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, field_validator


class MovieCreate(BaseModel):
  name: str
  rated: str
  total_rating: Optional[float]
  rating_total_count: Optional[int]
  runtime: int
  release_date: date
  budget: Optional[float]
  revenue: Optional[int]
  description: Optional[str]
  status: Optional[str]
  poster: Optional[str]
  country: str
  language: str
  genre_ids: list[int] = []
  

class MovieUpdate(BaseModel):
  name: Optional[str]
  rated: Optional[str]
  total_rating: Optional[float]
  rating_total_count: Optional[int]
  runtime: Optional[int]
  release_date: Optional[date]
  budget: Optional[float]
  revenue: Optional[int]
  description: Optional[str]
  status: Optional[str]
  poster: Optional[str]
  country: Optional[str]
  language: Optional[str]
  genres: Optional[list[int]]

class MovieResponse(BaseModel):
  id: int
  rated: str
  total_rating: Optional[float]
  rating_total_count: Optional[int]
  runtime: int
  release_date: date
  budget: Optional[float]
  revenue: Optional[int]
  description: Optional[str]
  status: str
  poster: Optional[str]
  country: str
  language: str
  genre_names: list[str] = []
  
  model_config = ConfigDict(from_attributes=True)
  