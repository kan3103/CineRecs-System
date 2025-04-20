from fastapi import APIRouter

from router.controller import user, movie

api_router = APIRouter()
api_router.include_router(user.router)
api_router.include_router(movie.router)


