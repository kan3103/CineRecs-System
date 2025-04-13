from fastapi import APIRouter

from router.controller import movie
# from app.core.config import settings


api_router = APIRouter()
api_router.include_router(movie.router, prefix="/movies")


