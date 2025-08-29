import json
import os
from pathlib import Path
from typing import Any, Dict, List, TypeVar
from unittest.mock import mock_open, patch

import pandas as pd
import pytest

from src.config import decorator_spending_by_category, load_user_currencies, load_user_stocks, user_setting_path

# Тестовые данные
mock_user_settings = {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "GOOGL"]}

# Определим переменную типа
T = TypeVar("T", bound=Dict[str, Any])


# Создание тестового набора данных для транзакций
@pytest.fixture
def transactions() -> pd.DataFrame:
    return pd.DataFrame({"category": ["food", "entertainment", "food", "clothing"], "amount": [10.0, 20.0, 15.0, 5.0]})


def test_load_user_currencies() -> None:
    """Тестирование функции загрузки пользовательских валют."""
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_user_settings))):
        currencies = load_user_currencies()
        assert currencies == mock_user_settings["user_currencies"], "Должны получить корректный список валют"


def test_load_user_stocks() -> None:
    """Тестирование функции загрузки пользовательских акций."""
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_user_settings))):
        stocks = load_user_stocks()
        assert stocks == mock_user_settings["user_stocks"], "Должны получить корректный список акций"


def test_user_setting_path() -> None:
    """Проверка корректности пути к файлу с пользовательскими настройками."""
    assert user_setting_path.is_file(), "Путь к файлу user_settings.json должен существовать"


def test_data_directory() -> None:
    """Проверка корректности пути к директории с данными."""
    data_dir = Path(__file__).resolve().parent.parent / "data"
    assert data_dir.is_dir(), "Директория данных должна существовать"


def test_log_directory() -> None:
    """Проверка создания директории для логов."""
    log_dir = Path(__file__).resolve().parent.parent / "logs"
    assert log_dir.is_dir(), "Директория логов должна существовать"


# Тестирование декоратора без параметров
def test_spending_by_category_default_filename(transactions: pd.DataFrame) -> None:
    @decorator_spending_by_category()
    def spending_by_category(transactions: pd.DataFrame, category: str) -> List[Dict[str, Any]]:
        return transactions[transactions["category"] == category].to_dict(orient="records")

    result = spending_by_category(transactions, "food")
    assert result == [{"category": "food", "amount": 10.0}, {"category": "food", "amount": 15.0}]

    # Проверяем, что файл был создан
    assert os.path.exists("spending_by_category.json")

    with open("spending_by_category.json", "r", encoding="utf-8") as f:
        saved_result = json.load(f)

    assert saved_result == result

    # Удаляем файл после теста
    os.remove("spending_by_category.json")


# Тестирование декоратора с параметром
def test_spending_by_category_custom_filename(transactions: pd.DataFrame) -> None:
    @decorator_spending_by_category("test_report.json")
    def spending_by_category(transactions: pd.DataFrame, category: str) -> List[Dict[str, Any]]:
        return transactions[transactions["category"] == category].to_dict(orient="records")

    result = spending_by_category(transactions, "clothing")
    assert result == [{"category": "clothing", "amount": 5.0}]

    # Проверяем, что файл был создан с нужным именем
    assert os.path.exists("test_report.json")

    with open("test_report.json", "r", encoding="utf-8") as f:
        saved_result = json.load(f)

    assert saved_result == result

    # Удаляем файл после теста
    os.remove("test_report.json")


if __name__ == "__main__":
    pytest.main()
