

from sqlmodel import Field, Relationship, SQLModel


class MovieGenre(SQLModel, table=True):
  
  __tablename__ = 'dim_movie_genres'
  
  movie_id: int = Field(nullable=False, foreign_key='dim_movie.id', primary_key=True)
  genre_id: int = Field(nullable=False, foreign_key='dim_genres.id', primary_key=True)