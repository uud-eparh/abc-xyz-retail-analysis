"""
Загрузка Online Retail II в PostgreSQL.
Читает Excel (2 листа), объединяет, нормализует колонки.
Запуск: python scripts/load_data.py
"""

import sys
from pathlib import Path

import pandas as pd
import psycopg2

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from scripts.db_config import _get_conn_params  # noqa: E402

EXCEL_CANDIDATES = [
    ROOT_DIR / "data" / "online_retail_II.xlsx",
    ROOT_DIR / "data" / "online_retail_ii.xlsx",
    ROOT_DIR / "online_retail_II.xlsx",
]

TABLE_NAME = "raw_transactions"


def find_excel() -> Path:
    """Найти Excel с датасетом."""
    for path in EXCEL_CANDIDATES:
        if path.exists():
            return path
    raise FileNotFoundError(f"Файл online_retail_II.xlsx не найден. Искали: {EXCEL_CANDIDATES}")


def load_excel() -> pd.DataFrame:
    """Прочитать оба листа и объединить."""
    excel_path = find_excel()
    print(f"Читаем Excel: {excel_path}")

    xl = pd.ExcelFile(excel_path)
    print(f"Листы: {xl.sheet_names}")

    dfs = []
    for sheet in ["Year 2009-2010", "Year 2010-2011"]:
        if sheet in xl.sheet_names:
            df_sheet = pd.read_excel(excel_path, sheet_name=sheet)
            print(f"  {sheet}: {df_sheet.shape}")
            dfs.append(df_sheet)

    df = pd.concat(dfs, ignore_index=True)
    print(f"Объединено: {df.shape}")
    return df


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Привести колонки к snake_case."""
    print(f"Колонки в файле: {list(df.columns)}")

    rename_map = {}
    for col in df.columns:
        c = col.strip()
        if c in ("Invoice", "InvoiceNo"):
            rename_map[col] = "invoice_no"
        elif c == "StockCode":
            rename_map[col] = "stock_code"
        elif c == "Description":
            rename_map[col] = "description"
        elif c == "Quantity":
            rename_map[col] = "quantity"
        elif c in ("InvoiceDate", "Invoice Date"):
            rename_map[col] = "invoice_date"
        elif c in ("Price", "UnitPrice", "Unit Price"):
            rename_map[col] = "unit_price"
        elif c in ("Customer ID", "CustomerID", "Customer Id"):
            rename_map[col] = "customer_id"
        elif c == "Country":
            rename_map[col] = "country"

    df = df.rename(columns=rename_map)

    required = [
        "invoice_no",
        "stock_code",
        "description",
        "quantity",
        "invoice_date",
        "unit_price",
        "customer_id",
        "country",
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Отсутствуют колонки: {missing}")

    df["invoice_no"] = df["invoice_no"].astype(str)
    df["stock_code"] = df["stock_code"].astype(str)
    df["description"] = df["description"].astype(str)
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    df["customer_id"] = pd.to_numeric(df["customer_id"], errors="coerce").astype("Int64")
    df["country"] = df["country"].astype(str)

    return df


def main() -> None:
    """Основной сценарий: загрузка Excel → Postgres."""
    df = load_excel()
    df = normalize_columns(df)

    params = _get_conn_params()

    with psycopg2.connect(**params) as conn:
        with conn.cursor() as cur:
            # Пересоздаём таблицу
            cur.execute(f"DROP TABLE IF EXISTS {TABLE_NAME};")

            # DDL
            cur.execute(
                f"""
                CREATE TABLE {TABLE_NAME} (
                    invoice_no    text,
                    stock_code    text,
                    description   text,
                    quantity      integer,
                    invoice_date  timestamp,
                    unit_price    numeric,
                    customer_id   integer,
                    country       text
                );
            """
            )

            # Вставка через copy_expert (быстро!)
            import io

            buffer = io.StringIO()
            df.to_csv(buffer, index=False, header=False, sep="\t", na_rep="")
            buffer.seek(0)

            cur.copy_expert(
                f"COPY {TABLE_NAME} FROM STDIN WITH (FORMAT CSV, DELIMITER E'\\t', NULL '')", buffer
            )
        conn.commit()

    # Проверка
    with psycopg2.connect(**params) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {TABLE_NAME};")
            print(f"\n✅ Загружено строк: {cur.fetchone()[0]:,}")


if __name__ == "__main__":
    main()
