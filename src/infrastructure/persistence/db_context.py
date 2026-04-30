from collections.abc import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from src.shared.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    future=True,
    echo=False,
    pool_pre_ping=True,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_timeout=settings.database_pool_timeout_seconds,
    pool_recycle=settings.database_pool_recycle_seconds,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)


def ensure_database_ready() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
        connection.commit()


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def check_database_health() -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            connection.commit()
        return True
    except SQLAlchemyError:
        return False
