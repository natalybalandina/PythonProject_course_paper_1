import json
import logging
import os
from datetime import datetime

import pandas as pd

from src.utils import (
    analyzes_expenses,
    external_api_currency,
    external_api_stock,
    get_filtered_transactions,
    top_transactions,
)

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path_log_file = os.path.join(base_dir, "logs", "views.log")

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(path_log_file, "w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


def home_page(df_xls: pd.DataFrame, data: str, greeting: str) -> str:
    """Функция создает JSON-ответ на основе переданной даты и файла с транзакциями:
    1)приветствие; 2) общая сумма расходов и кешбэк по каждой карте; 3) топ-5 транзакций по сумме платежа;
    4) курс валют; 5) стоимость акций из S&P500."""

    logger.info(f"Функция {__name__} начала работу")
    try:
        date_obj = datetime.strptime(data, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        logger.error("Введен неверный формат даты.")
        raise ValueError("Неверный формат даты и времени. Используйте YYYY-MM-DD HH:MM:SS")
    try:
        logger.info("Формируем JSON-ответ с заданными данными")
        start_date = date_obj.replace(day=1)
        filtered_transaction = get_filtered_transactions(df_xls, date_obj, start_date)
        if not filtered_transaction.empty:
            expenses = analyzes_expenses(filtered_transaction)
            df_top_transactions = top_transactions(filtered_transaction)
        else:
            expenses = []
            df_top_transactions = []
        currency_rates = external_api_currency()
        stock_prices = external_api_stock()
        response = {
            "greeting": greeting,
            "cards": expenses,
            "top_transactions": df_top_transactions,
            "currency_rates": currency_rates,
            "stock_prices": stock_prices,
        }
        print(json.dumps(response, ensure_ascii=False, indent=4))
        return json.dumps(response, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"Возникла ошибка {e}", exc_info=True)
        print(type(e).__name__)
        return json.dumps(
            {"Error": "Неверный формат даты и времени. Используйте YYYY-MM-DD HH:MM:SS."}, ensure_ascii=False
        )
    finally:
        logger.info(f"Функция {__name__} завершила работу")

