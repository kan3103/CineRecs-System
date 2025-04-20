from fastapi import APIRouter

from router.controller import user, movie, genre, person

api_router = APIRouter()
api_router.include_router(user.router)
api_router.include_router(movie.router)
api_router.include_router(genre.router)
api_router.include_router(person.router)

