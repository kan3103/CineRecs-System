from fastapi import APIRouter, Depends, HTTPException, Body
from config.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from service.user import UserService, get_user_service
from service.dto.user import UserCreate, UserResponse, UserUpdate, UserLogin, LoginResponse
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

router = APIRouter(tags=["users"], prefix="/users")


@router.post('/', status_code=201, response_model=UserResponse)
async def create_user(dto: UserCreate, user_service: UserService = Depends(get_user_service)) -> UserResponse:
  try:
    user = await user_service.create_user(dto)
    return UserResponse.model_validate(user)
  except HTTPException as e:
    raise e

@router.get('/{id}', status_code=200, response_model=UserResponse)
async def get_user(id: int, user_service: UserService = Depends(get_user_service)) -> UserResponse:
  try:
    user = await user_service.get_user(id)
    return UserResponse.model_validate(user)
  except HTTPException as e:
    raise e

@router.put('/{id}', status_code=200, response_model=UserResponse)
async def update_user(id: int, dto: UserUpdate, user_service: UserService = Depends(get_user_service)) -> UserResponse:
  try:
    user = await user_service.update_user(id, dto)
    return UserResponse.model_validate(user)
  except HTTPException as e:
    raise e

@router.delete('/{id}', status_code=204, response_model=None)
async def delete_user(id: int, user_service: UserService = Depends(get_user_service)) -> None:
  try:
    await user_service.delete_user(id)
  except HTTPException as e:
    raise e

@router.post('/login', status_code=200, response_model=LoginResponse)
async def login(dto: UserLogin, user_service: UserService = Depends(get_user_service)) -> LoginResponse:
  try:
    result = await user_service.authenticate_user(dto.username, dto.password)
    return result
  except HTTPException as e:
    raise e

@router.post('/check-username', status_code=200)
async def check_username(username: str = Body(..., embed=True), user_service: UserService = Depends(get_user_service)) -> dict:
  try:
    exists = await user_service.username_exists(username)
    return {"exists": exists}
  except HTTPException as e:
    raise e

