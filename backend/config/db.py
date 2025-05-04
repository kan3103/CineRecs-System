from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from urllib.parse import quote_plus
import os



POSTGRES_USER = os.getenv("POSTGRES_USER", "avnadmin")
POSTGRES_PASSWORD = quote_plus(os.getenv("POSTGRES_PASSWORD", "AVNS_4QIAupJ-5VLHdr7KGKM"))
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "btl-data-mining-btl-data-mining.f.aivencloud.com")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "18362")
POSTGRES_DB = os.getenv("POSTGRES_DB", "defaultdb")

DATABASE_URL = (
  f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)
print(f"Connecting to database at {DATABASE_URL}")

engine = create_async_engine(DATABASE_URL, echo=True, pool_pre_ping=True, future=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def seed_db():
  async with engine.begin() as connection:
    print("Seeding database: creating tables if they do not exist-----------------------------------")
    from model.user import User
    from model.movie import Movie
    from model.genre import Genre
    from model.person import Person
    from model.credit import Credit
    from model.fact_movie_rating import FactMovieRating
   
    from model.movie_genre import MovieGenre
    
    from model.search_log import SearchLog
    

    await connection.run_sync(SQLModel.metadata.create_all)
    print("Database seeded successfully-------------------------------------------------------------")

async def get_session() -> AsyncGenerator[AsyncSession, None]:
  async with AsyncSessionLocal() as session:
    yield session

