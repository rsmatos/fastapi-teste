from fastapi import APIRouter
from .endpoints import curso

api_router = APIRouter()
api_router.include_router(curso.router, prefix="/cursos", tags=["cursos"])