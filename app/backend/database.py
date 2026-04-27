import os
from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_SQLITE_PATH = BASE_DIR / "beauty_agent.db"
_ENGINES: dict[str, Engine] = {}
_SESSION_FACTORIES: dict[str, sessionmaker[Session]] = {}


class Base(DeclarativeBase):
    pass


def normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)

    if database_url.startswith("postgresql://") and "+psycopg" not in database_url:
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    return database_url


def get_database_url() -> str:
    configured_url = os.getenv("DATABASE_URL")

    if configured_url:
        return normalize_database_url(configured_url)

    return f"sqlite:///{DEFAULT_SQLITE_PATH}"


def get_engine(database_url: str | None = None) -> Engine:
    resolved_url = database_url or get_database_url()

    if resolved_url not in _ENGINES:
        connect_args = {"check_same_thread": False} if resolved_url.startswith("sqlite") else {}
        _ENGINES[resolved_url] = create_engine(
            resolved_url,
            future=True,
            connect_args=connect_args,
        )

    return _ENGINES[resolved_url]


def get_session_factory(database_url: str | None = None) -> sessionmaker[Session]:
    resolved_url = database_url or get_database_url()

    if resolved_url not in _SESSION_FACTORIES:
        _SESSION_FACTORIES[resolved_url] = sessionmaker(
            bind=get_engine(resolved_url),
            autoflush=False,
            autocommit=False,
            future=True,
        )

    return _SESSION_FACTORIES[resolved_url]


def get_session() -> Session:
    session = get_session_factory()()

    try:
        yield session
    finally:
        session.close()


def init_database() -> None:
    from app.backend import db_models  # noqa: F401

    engine = get_engine()
    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    if "reviews" in inspector.get_table_names():
        existing_columns = {column["name"] for column in inspector.get_columns("reviews")}

        with engine.begin() as connection:
            if "category" not in existing_columns:
                connection.execute(
                    text("ALTER TABLE reviews ADD COLUMN category VARCHAR(50) DEFAULT 'skincare'")
                )

            connection.execute(
                text("UPDATE reviews SET category = 'skincare' WHERE category IS NULL")
            )


def reset_database_state() -> None:
    for engine in _ENGINES.values():
        engine.dispose()

    _ENGINES.clear()
    _SESSION_FACTORIES.clear()
