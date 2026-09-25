"""
Конфигурация подключения к PostgreSQL.
Использует psycopg2 (без SQLAlchemy).
Читает параметры из .env файла.
"""

import os
from pathlib import Path
from typing import Any

import pandas as pd
import psycopg2
from dotenv import load_dotenv

# Загружаем .env из корня проекта
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env", override=True)


def _get_conn_params() -> dict:
    """Собрать параметры подключения из .env."""
    return {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": int(os.getenv("POSTGRES_PORT", "5432")),
        "user": os.getenv("POSTGRES_USER", "abc_xyz"),
        "password": os.getenv("POSTGRES_PASSWORD", "abc_xyz_secret"),
        "dbname": os.getenv("POSTGRES_DB", "abc_xyz"),
    }


def read_sql(query: str, params: Any = None) -> pd.DataFrame:
    """
    Выполнить SELECT-запрос и вернуть DataFrame.

    Parameters
    ----------
    query : str
        SQL-запрос (параметры: %(name)s или %s).
    params : dict | tuple | None
        Параметры подстановки.

    Returns
    -------
    pd.DataFrame
    """
    with psycopg2.connect(**_get_conn_params()) as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if cur.description is None:
                return pd.DataFrame()
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
    return pd.DataFrame(rows, columns=columns)


def execute_sql(query: str, params: Any = None) -> None:
    """Выполнить SQL-команду (DDL/DML)."""
    with psycopg2.connect(**_get_conn_params()) as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
        conn.commit()


def execute_many(statements: list[str]) -> None:
    """Выполнить список SQL-команд в одной транзакции."""
    with psycopg2.connect(**_get_conn_params()) as conn:
        with conn.cursor() as cur:
            for stmt in statements:
                cur.execute(stmt)
        conn.commit()
