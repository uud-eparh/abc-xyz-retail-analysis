"""
Пайплайн анализа ассортимента Online Retail II.

Последовательный запуск этапов:
1. Загрузка данных
2. Очистка (sales)
3. ABC-анализ
4. XYZ-анализ
5. Матрица ABC/XYZ
6. Стратегии
7. Кандидаты
8. Оценка эффекта
"""

import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
NOTEBOOKS_DIR = ROOT_DIR / "notebooks"


def run_notebook(notebook_path: Path) -> None:
    """Запускает ноутбук и проверяет успешность выполнения."""
    print(f"Запуск {notebook_path.name}...")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "jupyter",
            "nbconvert",
            "--to",
            "notebook",
            "--execute",
            "--inplace",
            str(notebook_path),
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("Ошибка при выполнении ноутбука:")
        print(result.stderr)
        sys.exit(1)

    print("OK\n")


def main() -> None:
    """Запускает все ноутбуки по порядку."""
    notebooks = [
        "01_data_exploration.ipynb",
        "02_business_overview.ipynb",
        "03_abc_analysis.ipynb",
        "04_xyz_analysis.ipynb",
        "05_abc_xyz_matrix.ipynb",
        "06_strategy.ipynb",
        "07_candidates.ipynb",
        "08_impact_estimation.ipynb",
        "09_bonus_basket.ipynb",
        "10_bonus_bcg.ipynb",
        "11_bonus_basket.ipynb",
        "11b_basket_v2.ipynb",
    ]

    for nb_name in notebooks:
        nb_path = NOTEBOOKS_DIR / nb_name
        if not nb_path.exists():
            print(f"Ноутбук не найден: {nb_path}")
            sys.exit(1)
        run_notebook(nb_path)

    print("Пайплайн завершён успешно.")


if __name__ == "__main__":
    main()