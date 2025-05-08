from datetime import date
from sqlmodel import Field, Relationship, SQLModel
from typing import TYPE_CHECKING
import time

if TYPE_CHECKING:
  from model.movie import Movie
  from model.user import User


class FactMovieRating(SQLModel, table=True):
  
  __tablename__ = 'fact_movie_rating' # type: ignore
  
  user_id: int = Field(nullable=False, foreign_key="dim_user.id", primary_key=True)
  movie_id: int = Field(nullable=False, foreign_key="dim_movie.id", primary_key=True)
  rating: float = Field(nullable=False, ge=0.0, le=5.0)
  timestamp: int = Field(nullable=True, default_factory=lambda: int(time.time()))
  
  user: "User" = Relationship(back_populates='ratings')
  movie: "Movie" = Relationship(back_populates='ratings')
  
  # Add a property that converts the timestamp to a date if needed
  @property
  def date(self) -> date:
    """Convert integer timestamp to date object for response models"""
    from datetime import datetime
    if self.timestamp is None:
      return date.today()
    return datetime.fromtimestamp(self.timestamp).date()