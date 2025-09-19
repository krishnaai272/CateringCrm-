from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

# Single Base for all models
Base = declarative_base()

# -------------------------
# Async Engine
# -------------------------
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True
)

# -------------------------
# Async Session
# -------------------------
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency for FastAPI
async def get_db():
    async with async_session() as session:
        yield session