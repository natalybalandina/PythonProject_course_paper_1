import json
import logging
import os
from collections.abc import Callable
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Optional

import pandas as pd

from src.utils import get_filtered_transactions

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path_file_report = os.path.join(base_dir, "reports", "my_report.json")
path_log_file = os.path.join(base_dir, "logs", "reports.log")

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(path_log_file, "w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


def reports_decorator(filename: Optional[str] = None) -> Callable:
    """Декоратор для функций-отчетов, записывающий результат в файл,
    filename - имя файла для записи отчета. Если None, используется имя по умолчанию."""

    def my_decorator(func: Any) -> Any:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            nonlocal filename
            try:
                result = func(*args, **kwargs)
                if filename is None:
                    logger.info("Создаем директорию для отчета и формируем имя файла")
                    file_name = f"{func.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    filename = os.path.join(base_dir, "reports", file_name)
                    os.makedirs(os.path.dirname(filename), exist_ok=True)
                logger.info(f"Записываем результат работы функции {func.__name__} в файл")
                with open(filename, "w", encoding="utf-8") as file:
                    json.dump(result.to_dict(orient="records"), file, ensure_ascii=False, indent=4)
                logger.info(f"Данные успешно записаны в файл: {filename}")
                print(f"Данные успешно записаны в файл: {filename}")
                return result
            except TypeError as error:
                logger.error(f"Данные не были записаны в файл,ошибка {error.__class__.__name__}", exc_info=True)
                print(f"Данные не были записаны в файл из-за ошибки {error.__class__.__name__}")

        return wrapper

    return my_decorator


@reports_decorator(filename=path_file_report)
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Функция возвращает траты по заданной категории за последние три месяца (от переданной даты)."""
    logger.info(f"Функция {__name__} начала работу")
    if date is None:
        date_obj = datetime.now()
    else:
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            logger.info("Введен неверный формат даты.")
            raise ValueError("Неверный формат даты и времени. Используйте YYYY-MM-DD HH:MM:SS")
    try:
        start_date = date_obj - timedelta(days=90)
        logger.info("Фильтруем совершенные расходы за последние три месяца от переданной даты")
        filtered_transactions = get_filtered_transactions(transactions, date_obj, start_date)
        if filtered_transactions.empty:
            logger.info("Нет расходов за выбранный период.")
            return pd.DataFrame()
        filtered_transactions["Дата операции"] = filtered_transactions["Дата операции"].dt.strftime("%d.%m.%Y")
        result_transactions = pd.DataFrame(
            filtered_transactions[(filtered_transactions["Категория"].str.upper() == category.upper())]
        )
        if result_transactions.empty:
            logger.info(f"По категории '{category}' за выбранный период не было расходов.")
            print(f"По категории '{category}' за выбранный период не было расходов.")
            return pd.DataFrame()
        result_transactions = result_transactions[["Дата операции", "Категория", "Сумма операции", "Описание"]]
        return result_transactions
    except Exception as e:
        print(type(e).__name__)
        logger.error(f"Возникла ошибка {e}", exc_info=True)
        return pd.DataFrame()
    finally:
        logger.info(f"Функция {__name__} завершила работу")

