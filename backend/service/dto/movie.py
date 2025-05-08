
from datetime import date
from typing import TYPE_CHECKING, Optional
from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, field_validator
from service.dto.genre import GenreResponse


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

class MovieQuery(BaseModel):
  name: Optional[str] = None
  rated: Optional[str] = None 
  min_total_rating: Optional[float] = None
  max_total_rating: Optional[float] = None
  min_runtime: Optional[int] = None
  max_runtime: Optional[int] = None
  from_release_date: Optional[date] = None
  to_release_date: Optional[date] = None
  min_revenue: Optional[int] = None
  max_revenue: Optional[int] = None
  description: Optional[str] = None
  status: Optional[str] = None
  countries: Optional[list[str]] = None
  languages: Optional[list[str]] = None
  

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
  name: str
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
  genres: list[GenreResponse] = []
  
  model_config = ConfigDict(from_attributes=True)