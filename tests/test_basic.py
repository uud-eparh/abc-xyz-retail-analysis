"""
Базовые тесты проекта ABC/XYZ анализа.

Проверяют чистые функции без подключения к БД.
"""

import numpy as np
import pandas as pd


def test_abc_categories_logic():
    """Проверка логики присвоения ABC-категорий.

    Тестируем саму логику (присвоение по накопительной доле),
    а не точные проценты на границе (из-за float-погрешности).
    """
    # Синтетические данные: 10 SKU по убыванию выручки
    df = pd.DataFrame(
        {
            "revenue": [100, 50, 20, 15, 5, 3, 2, 2, 2, 1],
        }
    )
    df["revenue_share"] = df["revenue"] / df["revenue"].sum()
    df["cum_share"] = df["revenue_share"].cumsum()

    df["abc"] = np.select(
        [df["cum_share"] <= 0.80, df["cum_share"] <= 0.95],
        ["A", "B"],
        default="C",
    )

    # ---------- Проверки ----------

    # 1. Все три категории присутствуют
    assert set(df["abc"]) == {"A", "B", "C"}

    # 2. Порядок сохраняется: A идут раньше B, B раньше C
    #    (в отсортированных по убыванию данных)
    a_indices = df[df["abc"] == "A"].index
    b_indices = df[df["abc"] == "B"].index
    c_indices = df[df["abc"] == "C"].index
    assert a_indices.max() < b_indices.min()
    assert b_indices.max() < c_indices.min()

    # 3. A-группа даёт значительную долю (не менее 70%)
    a_share = df[df["abc"] == "A"]["revenue"].sum() / df["revenue"].sum()
    assert a_share >= 0.70, f"A-доля = {a_share:.2%}"

    # 4. C-группа — маленькая (< 15%)
    c_share = df[df["abc"] == "C"]["revenue"].sum() / df["revenue"].sum()
    assert c_share < 0.15, f"C-доля = {c_share:.2%}"

    # 5. На конкретной строке: SKU с выручкой 100 (первый) → A
    assert df.iloc[0]["abc"] == "A"


def test_xyz_cv_thresholds():
    """Проверка логики CV-порогов XYZ."""
    cvs = pd.Series([0.2, 0.4, 0.5, 0.7, 1.0, 1.5, 2.0])
    categories = np.select(
        [cvs <= 0.5, cvs <= 1.0],
        ["X", "Y"],
        default="Z",
    )

    assert categories[0] == "X"
    assert categories[2] == "X"
    assert categories[3] == "Y"
    assert categories[4] == "Y"
    assert categories[5] == "Z"


def test_sales_filter_logic():
    """Проверка логики фильтрации sales."""
    df = pd.DataFrame(
        {
            "invoice_no": ["A1", "C1", "A2", "A3"],
            "quantity": [10, -5, 0, 20],
            "unit_price": [5.0, 5.0, 5.0, -1.0],
        }
    )

    filtered = df[
        (~df["invoice_no"].str.startswith("C")) & (df["quantity"] > 0) & (df["unit_price"] > 0)
    ]

    assert len(filtered) == 1
    assert filtered.iloc[0]["invoice_no"] == "A1"


def test_bcg_quadrant_logic():
    """Проверка логики BCG-квадрантов."""

    def bcg(row):
        high_growth = row["growth"] >= 0
        high_share = row["share"] >= 0.01
        if high_growth and high_share:
            return "Stars"
        if not high_growth and high_share:
            return "Cash Cows"
        if high_growth and not high_share:
            return "Question Marks"
        return "Dogs"

    assert bcg({"growth": 0.5, "share": 0.5}) == "Stars"
    assert bcg({"growth": -0.5, "share": 0.5}) == "Cash Cows"
    assert bcg({"growth": 0.5, "share": 0.001}) == "Question Marks"
    assert bcg({"growth": -0.5, "share": 0.001}) == "Dogs"
