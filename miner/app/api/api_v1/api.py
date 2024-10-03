from fastapi import APIRouter

from app.api.api_v1.endpoints import currency


api_router = APIRouter()
api_router.include_router(currency.router, prefix="/currencies", tags=["currencies"])