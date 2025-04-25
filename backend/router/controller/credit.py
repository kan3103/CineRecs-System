
from fastapi import APIRouter, Depends, HTTPException

from service.credit import CreditService, get_credit_service
from service.dto.credit import CreaditUpdate, CreditCreate, CreditResponse


router = APIRouter(tags=["credits"], prefix="/credits")

@router.post('/', response_model=CreditResponse, status_code=201)
async def create_credit(dto: CreditCreate, credit_service: CreditService = Depends(get_credit_service)) -> CreditResponse:
  try:
    credit = await credit_service.create_credit(dto)
    return CreditResponse.model_validate(credit)
  except HTTPException as e:
    raise e

@router.put('/{id}', response_model=CreditResponse, status_code=200)
async def update_credit(id: int, dto: CreaditUpdate, credit_service: CreditService = Depends(get_credit_service)) -> CreditResponse:
  try:
    credit = await credit_service.update_credit(id, dto)
    return CreditResponse.model_validate(credit)
  except HTTPException as e:
    raise e

@router.get('/{id}', response_model=CreditResponse, status_code=200)
async def get_credit(id: int, credit_service: CreditService = Depends(get_credit_service)) -> CreditResponse:
  try:
    credit = await credit_service.get_credit(id)
    return CreditResponse.model_validate(credit)
  except HTTPException as e:
    raise e

@router.delete('/{id}', response_model=None, status_code=204)
async def delete_credit(id: int, credit_service: CreditService = Depends(get_credit_service)) -> None:
  try:
    await credit_service.delete_credit(id)
  except HTTPException as e:
    raise e
  