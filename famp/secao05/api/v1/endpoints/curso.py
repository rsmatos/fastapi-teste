from typing import List

from fastapi import APIRouter, status, HTTPException, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from models.curso_model import CursoModel
from core.dependencies import get_session

from sqlmodel.sql.expression import Select, SelectOfScalar

SelectOfScalar.inherit_cache = True
Select.inherit_cache = True

router = APIRouter()


@router.post("/", response_model=CursoModel, status_code=status.HTTP_201_CREATED)
async def post_curso(curso: CursoModel, db: AsyncSession = Depends(get_session)):
    db.add(curso)
    await db.commit()

    return curso


@router.get("/", response_model=List[CursoModel], status_code=status.HTTP_200_OK)
async def get_cursos(db: AsyncSession = Depends(get_session)) -> List[CursoModel]:
    async with db as session:
        result = await session.execute(select(CursoModel).order_by(CursoModel.id))
        return result.scalars().all()


@router.get("/{curso_id}", response_model=CursoModel, status_code=status.HTTP_200_OK)
async def get_curso(curso_id: int, db: AsyncSession = Depends(get_session)):
    async with db as session:
        result = await find_curso_by_id(curso_id, session)

        curso = result.scalar_one_or_none()

        await raise_exception_if_not_found(curso)

        return curso


@router.put("/{curso_id}", response_model=CursoModel, status_code=status.HTTP_202_ACCEPTED)
async def put_curso(curso_id: int, curso: CursoModel, db: AsyncSession = Depends(get_session)):
    async with db as session:
        result = await find_curso_by_id(curso_id, session)
        curso_db = result.scalar_one_or_none()
        await raise_exception_if_not_found(curso)

        curso_db.titulo = curso.titulo
        curso_db.horas = curso.horas
        curso_db.aulas = curso.aulas

        await session.commit()

        return curso_db


@router.delete("/{curso_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_curso(curso_id: int, db: AsyncSession = Depends(get_session)):
    async with db as session:
        result = await find_curso_by_id(curso_id, session)
        curso = result.scalar_one_or_none()
        await raise_exception_if_not_found(curso)

        await session.delete(curso)
        await session.commit()

        return Response(status_code=status.HTTP_204_NO_CONTENT)


async def find_curso_by_id(curso_id, session):
    result = await session.execute(select(CursoModel).filter(CursoModel.id == curso_id))
    return result


async def raise_exception_if_not_found(curso):
    if not curso:
        raise HTTPException(detail="Curso não encontrado", status_code=status.HTTP_404_NOT_FOUND)
