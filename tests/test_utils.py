from datetime import datetime
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pandas as pd
import requests
from _pytest.capture import CaptureFixture

from src.utils import (
    analyzes_expenses,
    external_api_currency,
    external_api_stock,
    get_filtered_transactions,
    get_greeting,
    get_read_excel,
    top_transactions,
)


@patch("pandas.read_excel")
def test_get_read_excel(mock_read_excel: MagicMock) -> None:
    """Тестируем чтение EXCEL-файла"""
    transaction_dict = {"key1": ["value1", "value2"], "key2": ["value1", "value2"]}
    mock_read_excel.return_value = pd.DataFrame(transaction_dict)
    assert get_read_excel("test.xlsx") == [{"key1": "value1", "key2": "value1"}, {"key1": "value2", "key2": "value2"}]
    mock_read_excel.assert_called_once()


def test_get_read_excel_empty() -> None:
    """Проверяем работу функции, если файл пустой"""
    result = get_read_excel("data/orders_empty.xlsx")
    assert result == []


def test_get_read_excel_not_found() -> None:
    """Проверяем работу функции, если файл не найден"""
    result = get_read_excel("data/orders_empty1.xlsx")
    assert result == []


@patch("requests.get")
def test_external_api_currency(mock_get: MagicMock) -> None:
    """Проверяем результат обработки запроса к внешнему API для получения текущего курса валют"""
    mock_response = mock_get.return_value
    mock_get.return_value.status_code = 200
    mock_response.json.side_effect = [{"info": {"rate": 103.123532}}, {"info": {"rate": 106.217105}}]
    assert external_api_currency() == [{"currency": "USD", "rate": 103.12}, {"currency": "EUR", "rate": 106.22}]
    assert mock_get.call_count == 2


@patch("requests.get")
def test_external_api_currency_invalid(mock_get: MagicMock) -> None:
    """Проверка некорректного завершения обработки запроса к внешнему API для получения текущего курса валют"""
    mock_response = mock_get.return_value
    mock_get.return_value.status_code = 400
    mock_response.json.side_effect = []
    assert external_api_currency() == []
    assert mock_get.call_count == 2


@patch("requests.get")
def test_external_api_currency_request_exception(mock_get: MagicMock) -> None:
    """Проверяем обработку исключения requests.exceptions.RequestException"""
    mock_get.side_effect = requests.exceptions.RequestException("Ошибка запроса")
    result = external_api_currency()
    assert result == []
    assert mock_get.call_count > 0


@patch("src.utils.requests.get")
def test_external_api_stock(mock_get: MagicMock) -> None:
    """Проверяем результат обработки запроса к внешнему API для получения цен на акции"""
    mock_response = mock_get.return_value
    mock_get.return_value.status_code = 200
    mock_response.json.side_effect = [
        {"results": [{"c": 150.12}]},
        {"results": [{"c": 3173.18}]},
        {"results": [{"c": 2742.39}]},
        {"results": [{"c": 296.71}]},
        {"results": [{"c": 1007.08}]},
    ]
    assert external_api_stock() == [
        {"stock": "AAPL", "price": 150.12},
        {"stock": "AMZN", "price": 3173.18},
        {"stock": "GOOGL", "price": 2742.39},
        {"stock": "MSFT", "price": 296.71},
        {"stock": "TSLA", "price": 1007.08},
    ]
    assert mock_get.call_count == 5


@patch("src.utils.requests.get")
def test_external_api_stock_invalid(mock_get: MagicMock) -> None:
    """Проверка некорректного завершения обработки запроса к внешнему API для получения цен на акции"""
    mock_response = mock_get.return_value
    mock_get.return_value.status_code = 400
    mock_response.json.side_effect = []
    assert external_api_stock() == []
    assert mock_get.call_count == 5


@patch("src.utils.requests.get")
def test_external_api_stock_request_exception(mock_get: MagicMock) -> None:
    """Проверяем обработку исключения requests.exceptions.RequestException"""
    mock_get.side_effect = requests.exceptions.RequestException("Ошибка запроса")
    result = external_api_stock()
    assert result == []
    assert mock_get.call_count > 0


@patch("src.utils.datetime")
def test_get_greeting_(mock_datetime: MagicMock) -> None:
    """Тестируем функцию приветствия в зависимости от времени суток"""
    mock_datetime.now.return_value = datetime(2021, 12, 30, 4, 20, 55)
    assert get_greeting(mock_datetime.now()) == "Доброй ночи"


@patch("src.utils.datetime")
def test_get_greeting_1(mock_datetime: MagicMock) -> None:
    """Тестируем функцию приветствия в зависимости от времени суток"""
    mock_datetime.now.return_value = datetime(2021, 12, 30, 11, 59, 55)
    assert get_greeting(mock_datetime.now()) == "Доброе утро"


@patch("src.utils.datetime")
def test_get_greeting_2(mock_datetime: MagicMock) -> None:
    """Тестируем функцию приветствия в зависимости от времени суток"""
    mock_datetime.now.return_value = datetime(2021, 12, 30, 14, 20, 55)
    assert get_greeting(mock_datetime.now()) == "Добрый день"


@patch("src.utils.datetime")
def test_get_greeting_3(mock_datetime: MagicMock) -> None:
    """Тестируем функцию приветствия в зависимости от времени суток"""
    mock_datetime.now.return_value = datetime(2021, 12, 30, 23, 20, 55)
    assert get_greeting(mock_datetime.now()) == "Добрый вечер"


def test_analyzes_expenses(test_transactions: List[Dict[str, Any]]) -> None:
    """Тестируем поведение функции, которая возвращает общую сумму расходов и размер кэшбэка
    по каждой карте за указанный период"""
    result = analyzes_expenses(pd.DataFrame(test_transactions))
    assert result == [{"last_digits": "7197", "total_spent": 224.89, "cashback": 2.0}]


def test_analyzes_expenses_exception(test_transactions: List[Dict[str, Any]]) -> None:
    """Тестируем отработку исключения"""
    with patch("pandas.DataFrame.groupby") as mock_groupby:
        mock_groupby.side_effect = Exception("Ошибка при группировке")
        result = analyzes_expenses(pd.DataFrame(test_transactions))
        assert result == []


def test_get_filtered_transactions(test_transactions: List[Dict[str, Any]]) -> None:
    """Тестируем результативное поведение функции, которая фильтрует полученный DataFrame по дате и статусу операции
    и принимает во внимание только расходы"""
    date_obj = datetime.strptime("2021-12-31 00:00:00", "%Y-%m-%d %H:%M:%S")
    start_date = date_obj.replace(day=1)
    result = get_filtered_transactions(pd.DataFrame(test_transactions), date_obj, start_date)
    expected_df = pd.DataFrame(test_transactions)
    expected_df["Дата операции"] = pd.to_datetime(expected_df["Дата операции"], dayfirst=True).dt.normalize()
    pd.testing.assert_frame_equal(result, expected_df)


def test_get_filtered_transactions_empty(capsys: CaptureFixture[str], test_transactions: List[Dict[str, Any]]) -> None:
    """Тестируем нулевой результат функции, которая фильтрует полученный DataFrame по дате и статусу операции
    и принимает во внимание только расходы"""
    date_obj = datetime.strptime("2024-12-31 00:00:00", "%Y-%m-%d %H:%M:%S")
    start_date = date_obj.replace(day=1)
    result = get_filtered_transactions(pd.DataFrame(test_transactions), date_obj, start_date)
    captured = capsys.readouterr()
    assert captured.out == "Нет расходов за выбранный период.\n"
    assert result.empty


def test_get_filtered_transactions_invalid_data() -> None:
    """Тестируем поведение функции при исключении"""
    invalid_transactions = pd.DataFrame(
        {"Дата операции": ["нет данных"], "Номер карты": ["1234"], "Статус": ["OK"], "Сумма операции": [-100]}
    )
    date_obj = datetime.strptime("2024-12-31 00:00:00", "%Y-%m-%d %H:%M:%S")
    start_date = date_obj.replace(day=1)
    result = get_filtered_transactions(invalid_transactions, date_obj, start_date)
    assert result.empty


def test_top_transactions(test_transactions: List[Dict[str, Any]]) -> None:
    """Тестируем функцию, которая возвращает список словарей с Топ-5 транзакциями по сумме платежа."""
    expected_df = pd.DataFrame(test_transactions)
    expected_df["Дата операции"] = pd.to_datetime(expected_df["Дата операции"], dayfirst=True).dt.normalize()
    result = top_transactions(expected_df)
    assert result == [
        {"date": "31.12.2021", "amount": 160.89, "category": "Супермаркеты", "description": "Колхоз"},
        {"date": "31.12.2021", "amount": 64.0, "category": "Ж/д билеты", "description": "Колхоз"},
    ]


def test_top_transactions_invalid_data() -> None:
    """Тестируем поведение функции при исключении"""
    invalid_transactions = pd.DataFrame(
        {
            "Дата операции": ["нет данных"],
            "Категория": ["Ж/д билеты"],
            "Описание": ["Колхоз"],
            "Сумма операции": [-100],
        }
    )
    result = top_transactions(invalid_transactions)
    assert result == []
