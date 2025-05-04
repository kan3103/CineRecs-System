
from sqlmodel import Field, Relationship, SQLModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from model.movie import Movie
  from model.person import Person


class Credit(SQLModel, table=True):
  
  __tablename__ = 'dim_credits' # type: ignore
  
  movie_id: int = Field(nullable=False, foreign_key="dim_movie.id", primary_key=True)
  person_id: int = Field(nullable=False, foreign_key='dim_person.id', primary_key=True)
  role: str = Field(nullable=False, max_length=255)
  job: str = Field(nullable=False)
  
  person: "Person" = Relationship(back_populates='credits')
  movie: "Movie" = Relationship(back_populates='credits')
  