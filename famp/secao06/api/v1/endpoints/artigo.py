from typing import List
from fastapi import APIRouter, status, Depends, HTTPException, Response

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.artigo_model import ArtigoModel
from models.usuario_model import UsuarioModel
from schemas.artigo_schema import ArtigoSchema
from core.dependencies import get_session, get_usuario_atual

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ArtigoSchema)
async def post_artigo(artigo: ArtigoSchema, usuario_logado: UsuarioModel = Depends(get_usuario_atual),
                      db: AsyncSession = Depends(get_session)):
    novo_artigo: ArtigoModel = ArtigoModel(titulo=artigo.titulo, descricao=artigo.descricao,
                                           url_fonte=artigo.url_fonte, usuario_id=usuario_logado.id)
    db.add(novo_artigo)
    await db.commit()

    return novo_artigo


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[ArtigoSchema])
async def get_artigos(db: AsyncSession = Depends(get_session)) -> List[ArtigoSchema]:
    async with db as session:
        query = select(ArtigoModel)
        result = await session.execute(query)
        return result.scalars().unique().all()


@router.get("/{artigo_id}", status_code=status.HTTP_200_OK, response_model=ArtigoSchema)
async def get_artigo(artigo_id: int, db: AsyncSession = Depends(get_session)):
    async with db as session:
        result = await find_artigo_by_id(artigo_id, session)
        artigo: ArtigoModel = result.scalars().unique().one_or_none()

        await raise_exception_if_artigo_not_found(artigo)

        return artigo


@router.put("/{artigo_id}", status_code=status.HTTP_202_ACCEPTED, response_model=ArtigoSchema)
async def update_artigo(artigo_id: int, artigo: ArtigoSchema, db: AsyncSession = Depends(get_session),
                        usuario_logado: UsuarioModel = Depends(get_usuario_atual)):
    async with db as session:
        result = await find_artigo_by_id(artigo_id, session)
        artigo_update: ArtigoModel = result.scalars().unique().one_or_none()

        await raise_exception_if_artigo_not_found(artigo_update)

        if artigo.titulo:
            artigo_update.titulo = artigo.titulo
        if artigo.descricao:
            artigo_update.descricao = artigo.descricao
        if artigo.url_fonte:
            artigo_update.url_fonte = artigo.url_fonte
        if usuario_logado.id != artigo_update.usuario_id:
            artigo_update.usuario_id = usuario_logado.id

        await session.commit()

        return artigo_update


@router.delete("/{artigo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_curso(artigo_id: int, db: AsyncSession = Depends(get_session),
                       usuario_logado: UsuarioModel = Depends(get_usuario_atual)):
    async with db as session:
        query = select(ArtigoModel).filter(ArtigoModel.id == artigo_id).filter(UsuarioModel.id == usuario_logado.id)
        result = await session.execute(query)
        artigo: ArtigoModel = result.scalars().unique().one_or_none()

        await raise_exception_if_artigo_not_found(artigo)

        await session.delete(artigo)
        await session.commit()

        return Response(status_code=status.HTTP_204_NO_CONTENT)


async def raise_exception_if_artigo_not_found(artigo):
    if not artigo:
        raise HTTPException(detail="Artigo não encontrado", status_code=status.HTTP_404_NOT_FOUND)


async def find_artigo_by_id(artigo_id, session):
    query = select(ArtigoModel).filter(ArtigoModel.id == artigo_id)
    result = await session.execute(query)
    return result
