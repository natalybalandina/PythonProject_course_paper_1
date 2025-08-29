import json
import os
from typing import Any, Dict, List
from unittest.mock import mock_open, patch

import pandas as pd
import pytest
from _pytest.capture import CaptureFixture

from src.reports import reports_decorator, spending_by_category

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path_file_report = os.path.join(base_dir, "reports", "my_report.json")


def test_spending_by_category(test_transactions: List[Dict[str, Any]]) -> None:
    """Тестируем запись в файл после успешного выполнения функции"""
    spending_by_category(pd.DataFrame(test_transactions), "Супермаркеты", "2021-12-31 00:00:00")
    with open(path_file_report, "r", encoding="utf-8") as file:
        result = file.read()
    assert (
        result == "[\n"
        "    {\n"
        '        "Дата операции": "31.12.2021",\n'
        '        "Категория": "Супермаркеты",\n'
        '        "Сумма операции": -160.89,\n'
        '        "Описание": "Колхоз"\n'
        "    }\n"
        "]"
    )


def test_spending_by_category_func(test_transactions: List[Dict[str, Any]]) -> None:
    """Тестируем поведение самой функции при корректных входных данных"""
    result = spending_by_category(pd.DataFrame(test_transactions), "Супермаркеты", "2021-12-31 00:00:00")
    result_dict = result.to_dict(orient="records")
    assert result_dict == [
        {"Дата операции": "31.12.2021", "Категория": "Супермаркеты", "Сумма операции": -160.89, "Описание": "Колхоз"}
    ]


def test_spending_by_category_func1(test_transactions: List[Dict[str, Any]]) -> None:
    """Тестируем поведение самой функции, когда регистр входных данных отличается"""
    result = spending_by_category(pd.DataFrame(test_transactions), "супермаркеты", "2021-12-31 00:00:00")
    result_dict = result.to_dict(orient="records")
    assert result_dict == [
        {"Дата операции": "31.12.2021", "Категория": "Супермаркеты", "Сумма операции": -160.89, "Описание": "Колхоз"}
    ]


def test_spending_by_category_date_invalid(test_transactions: List[Dict[str, Any]]) -> None:
    """Тестируем поведение самой функции, когда неверный формат даты - вызываем ошибку"""
    with pytest.raises(ValueError) as exc_info:
        spending_by_category(pd.DataFrame(test_transactions), "супермаркеты", "2021.12.31 00:00:00")
    assert str(exc_info.value) == "Неверный формат даты и времени. Используйте YYYY-MM-DD HH:MM:SS"


def test_spending_by_category_func2(capsys: CaptureFixture[str], test_transactions: List[Dict[str, Any]]) -> None:
    """Тестируем поведение самой функции, когда результат нулевой"""
    result = spending_by_category(pd.DataFrame(test_transactions), "Аптеки", "2021-12-31 00:00:00")
    result_dict = result.to_dict(orient="records")
    captured = capsys.readouterr()
    assert captured.out == (
        "По категории 'Аптеки' за выбранный период не было расходов.\n"
        "Данные успешно записаны в файл: "
        "C:\\Users\\olliw\\PycharmProjects\\cource_Project_1\\reports\\my_report.json\n"
    )
    assert result_dict == []


def test_spending_by_category_func3(test_transactions: List[Dict[str, Any]]) -> None:
    """Тестируем поведение самой функции, когда в заданный период нет расходов"""
    result = spending_by_category(pd.DataFrame(test_transactions), "супермаркеты", "2024-12-31 00:00:00")
    result_dict = result.to_dict(orient="records")
    assert result_dict == []


def test_reports_decorator(test_transactions: List[Dict[str, Any]]) -> None:
    """Тестируем работу декоратора"""
    mocked_file = mock_open()
    with patch("builtins.open", mocked_file):
        result = spending_by_category(pd.DataFrame(test_transactions), "супермаркеты", "2021-12-31 00:00:00")
        result_dict = result.to_dict(orient="records")
        assert result_dict == [
            {
                "Дата операции": "31.12.2021",
                "Категория": "Супермаркеты",
                "Сумма операции": -160.89,
                "Описание": "Колхоз",
            }
        ]
        mocked_file.assert_called_once_with(path_file_report, "w", encoding="utf-8")
        write_calls = mocked_file().write.call_args_list
        written_data = "".join(call[0][0] for call in write_calls)
        expected_data = json.dumps(result_dict, ensure_ascii=False, indent=4)
        assert written_data == expected_data


def test_reports_decorator_type_error() -> None:
    """Тестируем обработку в декораторе исключения TypeError"""

    @reports_decorator(filename=path_file_report)
    def spending_by_category() -> pd.DataFrame:
        raise TypeError("Ошибка типа")

    with patch("builtins.print") as mocked_print:
        with patch("src.reports.logger.error") as mocked_logger_error:
            spending_by_category()
            mocked_print.assert_any_call("Данные не были записаны в файл из-за ошибки TypeError")
            mocked_logger_error.assert_called_once()


def test_spending_by_category_exception1() -> None:
    """Тестируем поведение самой функции при возникновении исключения"""
    invalid_transactions = pd.DataFrame(
        {
            "Дата операции": ["нет данных"],
            "Категория": ["Ж/д билеты"],
            "Описание": ["Колхоз"],
            "Сумма операции": [-100],
        }
    )
    result = spending_by_category(invalid_transactions, "Ж/д билеты", "2024-12-31 00:00:00")
    assert result.empty


def test_spending_by_category_exception(test_transactions: List[Dict[str, Any]]) -> None:
    """Тестируем отработку исключения"""
    with patch("src.utils.get_filtered_transactions", side_effect=Exception("Тестовое исключение")):
        result = spending_by_category(pd.DataFrame(test_transactions), "Ж/д билеты", "2024-12-31 00:00:00")
        assert result.empty

