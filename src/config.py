import json
import logging
import os
from pathlib import Path
from typing import Any, Callable, List, Optional

# Определяем корневую директорию проекта
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Путь к директории с данными
DATA_DIR = Path(PROJECT_ROOT) / "data"

# Путь к файлу операций
file_path = DATA_DIR / "operations.xlsx"

# Путь к директории с логами
LOG_DIR = Path(PROJECT_ROOT) / "logs"
os.makedirs(LOG_DIR, exist_ok=True)  # Создаем директорию для логов, если она не существует

# Файл логов
LOG_FILE = LOG_DIR / "app.log"

# Настройки логирования
logging.basicConfig(
    filename=str(LOG_FILE),  # Файл для логирования
    level=logging.INFO,  # Уровень логирования
    format="%(asctime)s - %(levelname)s - %(message)s",  # Формат сообщений
)

# Путь к файлу пользовательских настроек
user_setting_path = Path(PROJECT_ROOT) / "user_settings.json"


def load_user_currencies() -> List[str]:
    """Загружает пользовательские валюты из файла user_settings.json."""
    try:
        with open(user_setting_path, encoding="utf-8") as file:
            content = json.load(file)
        return [currency for currency in content.get("user_currencies", []) if isinstance(currency, str)]
    except Exception as e:
        logging.error(f"Ошибка при загрузке пользовательских валют: {e}")
        return []


def load_user_stocks() -> List[str]:
    """Загружает пользовательские акции из файла user_settings.json."""
    try:
        with open(user_setting_path, encoding="utf-8") as file:
            content = json.load(file)
        return [stock for stock in content.get("user_stocks", []) if isinstance(stock, str)]
    except Exception as e:
        logging.error(f"Ошибка при загрузке пользовательских акций: {e}")
        return []


def decorator_spending_by_category(report_filename: Optional[str] = None) -> Callable:
    """Декоратор, который логирует результат функции в файл по умолчанию spending_by_category.json,
    а также записывает сообщения в лог-файл."""

    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)
            # Определяем имя файла для записи
            filename = report_filename if report_filename else "spending_by_category.json"
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=4)
                logging.info(f"Результат функции {func.__name__} успешно записан в {filename}")
            except Exception as e:
                logging.error(f"Произошла ошибка при записи в файл: {e}")
            return result

        return wrapper

    return decorator
