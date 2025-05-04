

from sqlmodel import Field, Relationship, SQLModel
from typing import TYPE_CHECKING, Optional

from model.movie_genre import MovieGenre

if TYPE_CHECKING:
  from model.movie import Movie


class Genre(SQLModel, table=True):
  
  __tablename__ = 'dim_genres' # type: ignore
  
  id: int = Field(nullable=True, primary_key=True)
  type: str = Field(nullable=False, min_length=1, max_length=63)
  
  movies: list["Movie"] = Relationship(back_populates='genres', link_model=MovieGenre)
  