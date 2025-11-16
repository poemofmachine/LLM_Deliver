from fastapi import APIRouter

from ..schemas import TokenCreateRequest, TokenResponse
from ..services.memory import memory_service

router = APIRouter(prefix="/tokens", tags=["Auth"])


@router.post("", response_model=TokenResponse, status_code=201)
def create_token(payload: TokenCreateRequest):
    return memory_service.create_token(payload)
