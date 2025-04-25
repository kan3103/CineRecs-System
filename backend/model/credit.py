
from sqlmodel import Field, Relationship, SQLModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from model.movie import Movie
  from model.person import Person


class Credit(SQLModel, table=True):
  
  __tablename__ = 'dim_credits' # type: ignore
  
  id: int = Field(primary_key=True, default=None)
  movie_id: int = Field(nullable=False, foreign_key="dim_movie.id")
  person_id: int = Field(nullable=False, foreign_key='dim_person.id')
  job: str = Field(nullable=False, min_length=1, max_length=255)
  
  person: "Person" = Relationship(back_populates='credits')
  movie: "Movie" = Relationship(back_populates='credits')
  