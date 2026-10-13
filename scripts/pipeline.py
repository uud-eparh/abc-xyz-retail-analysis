"""
Единый пайплайн обработки данных.

Запуск: python scripts/pipeline.py
"""
from scripts.db_config import execute_sql, read_sql

# Параметры
START_DATE = "2009-12-01"
END_DATE = "2011-11-30"  # 24 полных месяца

def normalize_stock_codes():
    """Нормализация: UPPER(stock_code)."""
    execute_sql(f"""
        UPDATE raw_transactions
        SET stock_code = UPPER(stock_code);
    """)

def build_sales():
    """sales с единым периодом."""
    execute_sql(f"""
        CREATE TABLE sales AS
        SELECT
            UPPER(stock_code) AS stock_code,
            ...
        FROM raw_transactions
        WHERE
            invoice_no NOT LIKE 'C%'
            AND quantity > 0
            AND unit_price > 0
            AND invoice_date >= '{START_DATE}'
            AND invoice_date <= '{END_DATE}'
            ...
    """)

def build_candidates():
    """Кандидаты с учётом всех замечаний."""
    ...

# и т.д.