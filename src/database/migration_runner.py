from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Iterable

from sqlalchemy import text

from src.database.engine import engine


MIGRATIONS_DIR = Path(__file__).resolve().parents[2] / "migrations"


CREATE_MIGRATIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    id SERIAL PRIMARY KEY,
    filename TEXT UNIQUE NOT NULL,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


async def apply_migrations() -> None:
    if not MIGRATIONS_DIR.exists():
        raise FileNotFoundError(
            f"Каталог с миграциями не найден: {MIGRATIONS_DIR}"
        )

    migrations = sorted(MIGRATIONS_DIR.glob("*.sql"))

    async with engine.begin() as conn:
        check_table = await conn.execute(
            text(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'schema_migrations'
                )
                """
            )
        )
        table_exists = check_table.scalar()
        
        if not table_exists:
            await conn.execute(text(CREATE_MIGRATIONS_TABLE_SQL))

        result = await conn.execute(text("SELECT filename FROM schema_migrations"))
        applied = {row[0] for row in result}

        for migration in migrations:
            if migration.name in applied:
                continue

            statements = _split_sql_statements(migration.read_text(encoding="utf-8"))
            if not statements:
                continue

            for statement in statements:
                await conn.execute(text(statement))

            await conn.execute(
                text(
                    "INSERT INTO schema_migrations (filename) VALUES (:filename)"
                ),
                {"filename": migration.name},
            )


def _split_sql_statements(raw_sql: str) -> Iterable[str]:
    statements: list[str] = []
    current: list[str] = []

    for line in raw_sql.splitlines():
        cleared = line.strip()

        if not cleared or cleared.startswith("--"):
            continue

        current.append(line)

        if cleared.endswith(";"):
            statement = "\n".join(current).strip()
            if statement:
                statements.append(statement[:-1] if statement.endswith(";") else statement)
            current = []

    if current:
        statement = "\n".join(current).strip()
        if statement:
            statements.append(statement)

    return statements


if __name__ == "__main__":
    asyncio.run(apply_migrations())

