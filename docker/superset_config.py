"""
Конфигурация Superset для проекта ABC/XYZ анализа.
"""
import os

# Секретный ключ (в реальном проекте — через .env)
SECRET_KEY = os.getenv(
    "SUPERSET_SECRET_KEY",
    "abc_xyz_superset_secret_key_change_in_prod"
)

# Метаданные Superset хранятся в SQLite внутри volume
SQLALCHEMY_DATABASE_URI = "sqlite:////app/superset_home/superset.db"

# Не загружать примеры
LOAD_EXAMPLES = False

# Feature flags
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
    "DASHBOARD_NATIVE_FILTERS": True,
    "DASHBOARD_CROSS_FILTERS": True,
}

# Публичный доступ для упрощения демо
PUBLIC_ROLE_LIKE = "Gamma"

# Таймзона
DEFAULT_TIMEZONE = "Europe/Moscow"

# Отключаем Talisman (для локальной разработки)
TALISMAN_ENABLED = False