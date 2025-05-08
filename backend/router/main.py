from fastapi import APIRouter

from router.controller import user, movie, genre, person, credit, fact_movie_rating, recommendation, trending

api_router = APIRouter()
api_router.include_router(user.router)
api_router.include_router(movie.router)
api_router.include_router(genre.router)
api_router.include_router(person.router)
api_router.include_router(credit.router)
api_router.include_router(fact_movie_rating.router)
api_router.include_router(recommendation.router)
api_router.include_router(trending.router)
