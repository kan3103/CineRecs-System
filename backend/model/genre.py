

from sqlmodel import Field, Relationship, SQLModel
from typing import TYPE_CHECKING

from model.movie_genre import MovieGenre

if TYPE_CHECKING:
  from model.movie import Movie


class Genre(SQLModel, table=True):
  
  __tablename__ = 'dim_genres'
  
  id: int = Field(nullable=True, primary_key=True)
  type: str = Field(nullable=False, min_length=1, max_length=63)
  overall_rating: float = Field(nullable=True, default=0.0, ge=0.0, le=10.0)
  
  movies: list["Movie"] = Relationship(back_populates='genres', link_model=MovieGenre)
  