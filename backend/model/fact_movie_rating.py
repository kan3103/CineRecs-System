
from sqlmodel import Field, Relationship, SQLModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from model.movie import Movie
  from model.user import User


class FactMovieRating(SQLModel, table=True):
  
  __tablename__ = 'fact_movie_rating'
  id: int = Field(primary_key=True, default=None)
  user_id: int = Field(nullable=False, foreign_key="dim_user.id")
  movie_id: int = Field(nullable=False, foreign_key="dim_movie.id")
  rating: float = Field(nullable=False, ge=0.0, le=10.0)
  
  user: "User" = Relationship(back_populates='ratings')
  movie: "Movie" = Relationship(back_populates='movie')