
from datetime import date
from sqlmodel import Field, Relationship, SQLModel, Column
from sqlalchemy.dialects.postgresql import JSONB
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from model.fact_movie_rating import FactMovieRating
  from model.search_log import SearchLog


class User(SQLModel, table=True):
  
  __tablename__ = "dim_user"
  
  id: int = Field(default=None, primary_key=True)
  name: str = Field(nullable=False, min_length=1, max_length=255)
  date_of_birth: date = Field(nullable=False)
  username: str = Field(nullable=False, min_length=1, max_length=255)
  password: str = Field(nullable=False, min_length=1, max_length=255)
  created_at: date = Field(nullable=True, default=date.today(), allow_mutation=False)
  embedding: dict = Field(sa_column=Column(JSONB))
  
  search_logs: list["SearchLog"] = Relationship(back_populates='user')
  ratings: list["FactMovieRating"] = Relationship(back_populates='user')