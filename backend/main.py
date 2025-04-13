

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from config.db import seed_db
from router.main import api_router

def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"

API_PATH = "/api"
PROJECT_NAME = "Movie API"

@asynccontextmanager
async def lifespan(app: FastAPI):
  print('App is starting---------------------------------------------------------------------')
  seed_db()
  yield
  print('App is shutting down ---------------------------------------------------------------')

app = FastAPI(
  title=PROJECT_NAME,
  openapi_url=f"{API_PATH}/openapi.json",
  generate_unique_id_function=custom_generate_unique_id,
  lifespan=lifespan
)

  

app.include_router(api_router, prefix=API_PATH)