"""Fixtures compartilhadas: banco de dados PostgreSQL via testcontainers (integração/contrato)."""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator, Iterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.postgres import PostgresContainer

from app.main import app
from app.persistence.db import get_session
from app.persistence.models import Area, Base, Maquina, Planta, Ponto


@pytest.fixture(scope="session")
def postgres_container() -> Iterator[PostgresContainer]:
    with PostgresContainer("postgres:16") as container:
        yield container


@pytest_asyncio.fixture
async def test_engine(postgres_container: PostgresContainer) -> AsyncGenerator[AsyncEngine, None]:
    url = postgres_container.get_connection_url().replace("psycopg2", "asyncpg")
    engine = create_async_engine(url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(test_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(test_engine: AsyncEngine) -> AsyncGenerator[AsyncClient, None]:
    session_factory = async_sessionmaker(test_engine, expire_on_commit=False)

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def ponto_seed(db_session: AsyncSession) -> Ponto:
    """Cria hierarquia mínima (Planta > Área > Máquina > Ponto) para os testes."""
    planta = Planta(id=uuid.uuid4(), nome="Planta Teste")
    area = Area(id=uuid.uuid4(), planta_id=planta.id, nome="Área Teste")
    maquina = Maquina(id=uuid.uuid4(), area_id=area.id, nome="Máquina Teste")
    ponto = Ponto(id=uuid.uuid4(), maquina_id=maquina.id, nome="Ponto Teste")

    db_session.add_all([planta, area, maquina, ponto])
    await db_session.commit()
    await db_session.refresh(ponto)
    return ponto
