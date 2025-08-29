from typing import Any, Dict, List

from _pytest.capture import CaptureFixture

from src.services import analyze_cashback_categories


def test_analyze_cashback_categories(capsys: CaptureFixture[str], test_transactions: List[Dict[str, Any]]) -> None:
    """Тестируем работу функции, когда найдены транзакции в указанную дату"""
    result = analyze_cashback_categories(test_transactions, 2021, 12)
    captured = capsys.readouterr()
    assert captured.out == ("{\n" '    "Ж/д билеты": 70\n' "}\n")
    assert result == '{\n    "Ж/д билеты": 70\n}'


def test_analyze_cashback_categories_nul(capsys: CaptureFixture[str], test_transactions: List[Dict[str, Any]]) -> None:
    """Тестируем работу функции, когда не найдены транзакции в указанную дату"""
    result = analyze_cashback_categories(test_transactions, 2019, 12)
    captured = capsys.readouterr()
    assert captured.out == "За выбранный период нет транзакций с ненулевым кэшбэком\n"
    assert result == None


def test_analyze_cashback_categories_empty(capsys: CaptureFixture[str]) -> None:
    """Тестируем работу функции, когда словарь с данными о транзакциях пуст"""
    test_transaction: List[Dict[str, Any]] = []
    result = analyze_cashback_categories(test_transaction, 2021, 12)
    captured = capsys.readouterr()
    assert captured.out == "За выбранный период нет транзакций с ненулевым кэшбэком\n"
    assert result == None


def test_analyze_cashback_categories_type_error(capsys: CaptureFixture[str]) -> None:
    """Тестируем работу функции, когда ошибка в типе значения ключа 'Кэшбэк' - вызываем ошибку"""
    test_transactions_invalid = [
        {
            "Дата операции": "31.12.2021 16:44:00",
            "Дата платежа": "31.12.2021",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма операции": -160.89,
            "Валюта операции": "RUB",
            "Кэшбэк": 0,
            "Категория": "Супермаркеты",
        },
        {
            "Дата операции": "31.12.2021 16:42:04",
            "Дата платежа": "31.12.2021",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма операции": -64.0,
            "Валюта операции": "RUB",
            "Кэшбэк": "70",
            "Категория": "Ж/д билеты",
        },
    ]
    analyze_cashback_categories(test_transactions_invalid, 2021, 12)
    captured = capsys.readouterr()
    assert captured.out == "TypeError\n"

