from core.database import engine

from core.configs import settings


async def create_tables() -> None:
    import models.__all_models
    print("Criando as tabelas no banco de dados...")

    async with engine.begin() as connection:
        await connection.run_sync(settings.DBBaseModel.metadata.drop_all)
        await connection.run_sync(settings.DBBaseModel.metadata.create_all)

    print("Tabelas criadas com sucesso.")


if __name__ == "__main__":
    import asyncio

    asyncio.run(create_tables())
