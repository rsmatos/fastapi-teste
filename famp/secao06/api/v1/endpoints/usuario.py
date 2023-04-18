from typing import List, Optional, Any

import sqlalchemy.exc
from fastapi import APIRouter, status, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from models.usuario_model import UsuarioModel
from schemas.usuario_schema import UsuarioSchemaBase, UsuarioSchemaCreate, UsuarioSchemaArtigos, UsuarioSchemaUpdate

from core.dependencies import get_session, get_usuario_atual
from core.security import gerar_hash_senha
from core.auth import autenticar, criar_token_acesso

router = APIRouter()


@router.get("/logado", response_model=UsuarioSchemaBase, status_code=status.HTTP_200_OK)
def get_logado(usuario_logado: UsuarioModel = Depends(get_usuario_atual)):
    return usuario_logado


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=UsuarioSchemaBase)
async def post_usuario(usuario: UsuarioSchemaCreate, db: AsyncSession = Depends(get_session)):
    novo_usuario: UsuarioModel = UsuarioModel(nome=usuario.nome, sobrenome=usuario.sobrenome, email=usuario.email,
                                              senha=gerar_hash_senha(usuario.senha),
                                              eh_admin=usuario.eh_admin)

    async with db as session:
        try:
            session.add(novo_usuario)
            await session.commit()
            return novo_usuario
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail="Já existe um usuário com este e-mail cadastrado.")


@router.get("/", response_model=List[UsuarioSchemaBase], status_code=status.HTTP_200_OK)
async def get_usuarios(db: AsyncSession = Depends(get_session)) -> List[UsuarioSchemaBase]:
    async with db as session:
        query = select(UsuarioModel).order_by(UsuarioModel.id)
        result = await session.execute(query)
        return result.scalars().unique().all()


@router.get("/{usuario_id}", response_model=UsuarioSchemaArtigos, status_code=status.HTTP_200_OK)
async def get_usuario(usuario_id: int, db: AsyncSession = Depends(get_session)):
    async with db as session:
        result = await find_usuario_by_id(usuario_id, session)
        usuario: UsuarioSchemaArtigos = result.scalars().unique().one_or_none()

        await raise_exception_if_usuario_not_found(usuario)

        return usuario


@router.put("/{usuario_id}", response_model=UsuarioSchemaBase, status_code=status.HTTP_202_ACCEPTED)
async def put_usuario(usuario_id: int, usuario: UsuarioSchemaUpdate, db: AsyncSession = Depends(get_session)):
    async with db as session:
        result = await find_usuario_by_id(usuario_id, session)
        usuario_update = result.scalars().unique().one_or_none()

        await raise_exception_if_usuario_not_found(usuario_update)

        if usuario.nome:
            usuario_update.nome = usuario.nome
        if usuario.sobrenome:
            usuario_update.sobrenome = usuario.sobrenome
        if usuario.email:
            usuario_update.email = usuario.email
        if usuario.eh_admin:
            usuario_update.eh_admin = usuario.eh_admin
        if usuario.senha:
            usuario_update.senha = usuario.senha

        await session.commit()

        return usuario_update


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_usuario(usuario_id: int, db: AsyncSession = Depends(get_session)):
    async with db as session:
        result = await find_usuario_by_id(usuario_id, session)
        usuario = result.scalars().unique().one_or_none()

        await raise_exception_if_usuario_not_found(usuario)

        await session.delete(usuario)
        await session.commit()

        return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_session)):
    usuario = await autenticar(email=form_data.username, senha=form_data.password, db=db)

    if not usuario:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dados de acesso incorretos")

    return JSONResponse(content={"access_token": criar_token_acesso(sub=usuario.id), "token_type": "bearer"},
                        status_code=status.HTTP_200_OK)


async def find_usuario_by_id(usuario_id, session):
    query = select(UsuarioModel).filter(UsuarioModel.id == usuario_id)
    result = await session.execute(query)
    return result


async def raise_exception_if_usuario_not_found(usuario):
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
