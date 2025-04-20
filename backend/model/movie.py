from datetime import date
from sqlmodel import Field, Relationship, SQLModel, table

from typing import TYPE_CHECKING, Optional
from model.movie_genre import MovieGenre

if TYPE_CHECKING:
  
  from model.credit import Credit
  from model.fact_movie_rating import FactMovieRating
  from model.genre import Genre


class Movie(SQLModel, table=True):
  
  __tablename__ = "dim_movie" # type: ignore
  
  id: int = Field(default=None, primary_key=True)
  name: str = Field(nullable=False, min_length=1, max_length=255)
  rated: str = Field(nullable=False, min_length=1, max_length=15)
  total_rating: Optional[float] = Field(nullable=True, ge=0.0, le=10.0)
  rating_total_count: Optional[int] = Field(nullable=True, ge=0, default=0)
  runtime: str = Field(nullable=False, min_length=1, max_length=15, regex=r"^\d{1,3} min$")
  release_date: date = Field(nullable=False)
  budget: Optional[float] = Field(nullable=True, default=0.0, ge=0.0)
  revenue: str = Field(nullable=False, min_length=1, max_length=63, regex=r"^\$\d{1,3}(?:,\d{3})*$")
  description: Optional[str] = Field(nullable=True, max_length=1022, default='')
  status: bool = Field(nullable=False, default=True)
  poster: Optional[str] = Field(nullable= True, default = None)
  country: str = Field(nullable=False, min_length=1, max_length=255)
  language: str = Field(nullable=False, min_length=1, max_length=255)
  
  ratings: list["FactMovieRating"] = Relationship(back_populates='movie')
  genres: list["Genre"] = Relationship(back_populates='movies', link_model=MovieGenre)
  credits: list["Credit"] = Relationship(back_populates='movie')
