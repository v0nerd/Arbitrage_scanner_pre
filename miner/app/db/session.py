from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import settings
from app.db.base_class import Base

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    # required for sqlite
    connect_args={"check_same_thread": False},
)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# engine_async = create_async_engine(settings.AIOSQLALCHEMY_DATABASE_URI, echo=True)
# AsyncSessionLocal = async_sessionmaker(
#     bind=engine_async,
#     class_=AsyncSession,
#     autocommit=False,
#     autoflush=False,
# )
