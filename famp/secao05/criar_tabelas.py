from sqlmodel import SQLModel
from core.database import engine


async def create_tables() -> None:
    import models.__all_models
    print("Criando tabelas no banco de dados...")

    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.drop_all())
        await connection.run_sync(SQLModel.metadata.create_all())

    print("Tabelas criadas com sucesso...")


if __name__ == "__main__":
    import asyncio

    asyncio.run(create_tables())
