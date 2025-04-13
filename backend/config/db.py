from sqlmodel import SQLModel, create_engine, Session
from contextlib import contextmanager
from urllib.parse import quote_plus
import os



POSTGRES_USER = os.getenv("POSTGRES_USER", "khoango")
POSTGRES_PASSWORD = quote_plus(os.getenv("POSTGRES_PASSWORD", "Labr@DoR42#32$"))
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "cinema")

DATABASE_URL = (
  f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
  f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)
print(f"Connecting to database at {DATABASE_URL}")

engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True)

def seed_db():
  print("Seeding database: creating tables if they do not exist-----------------------------------")
  
  from model.movie import Movie
  from model.credit import Credit
  from model.fact_movie_rating import FactMovieRating
  from model.genre import Genre
  from model.movie_genre import MovieGenre
  from model.person import Person
  from model.search_log import SearchLog
  from model.user import User
  
  SQLModel.metadata.create_all(engine)
  print("Database seeded successfully-------------------------------------------------------------")

@contextmanager
def get_session():
  with Session(engine) as session:
    yield session
