from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["movies"])

@router.get('/')
def get_movies() -> int:
    return 1