"""
Alembic env.py – configured for Pothprohori.
Reads DATABASE_URL from .env and auto-imports all SQLAlchemy models
so `alembic revision --autogenerate` can detect schema changes.
"""
import os
import sys
from logging.config import fileConfig
from dotenv import load_dotenv

from sqlalchemy import engine_from_config, pool
from alembic import context

# ── Load .env so DATABASE_URL is available ──────────────────────────────────
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

# ── Make app importable ─────────────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ── Import all models so Alembic can detect them ────────────────────────────
from app.core.database import Base  # noqa: F401 – registers the engine
from app.models.user import User  # noqa: F401
from app.models.traffic import Violation, FineByState, LawSection  # noqa: F401
from app.models.chat_history import ChatHistory, ChatSession  # noqa: F401

# ── Alembic Config ───────────────────────────────────────────────────────────
config = context.config

# Override sqlalchemy.url from environment (ignores alembic.ini value)
# configparser uses % for interpolation — replace % with %% to escape
_db_url = os.getenv("DATABASE_URL", "").replace("%", "%%")
config.set_main_option("sqlalchemy.url", _db_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


# ── Offline mode (generate SQL without connecting) ───────────────────────────
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# ── Online mode (connect and migrate) ────────────────────────────────────────
def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
