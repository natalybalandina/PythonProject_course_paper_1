import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List

import pandas as pd
import requests

from dotenv import load_dotenv

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path_file_settings = os.path.join(base_dir, "data", "user_settings.json")
path_file_log = os.path.join(base_dir, "logs", "utils.log")

logging.basicConfig(
    level=logging.INFO,
    filename=path_file_log,
    filemode="w",
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
)
read_exel_logger = logging.getLogger("read_exel")
greeting_logger = logging.getLogger("greeting")
analyzes_expenses_logger = logging.getLogger("analyzes_expenses")
filtered_transactions_logger = logging.getLogger("filtered_transactions")
top_transactions_logger = logging.getLogger("top_transactions")
external_api_currency_logger = logging.getLogger("external_api_currency")
external_api_stock_logger = logging.getLogger("external_api_stock")

with open(path_file_settings) as f:
    settings = json.load(f)
user_currencies = settings["user_currencies"]
user_stocks = settings["user_stocks"]

load_dotenv()
API_KEY = os.getenv("API_KEY")
Base_URL = os.getenv("Base_URL")
API = os.getenv("API")


def get_read_excel(path_file_excel: str) -> List[Dict[str, Any]]:
    """Функция чтения EXCEL-файла"""
    try:
        read_exel_logger.info("Функция чтения EXCEL-файла начала работу")
        df_xls = pd.read_excel(path_file_excel)
        df_xls.fillna(0, inplace=True)
        dict_read_excel = df_xls.to_dict(orient="records")
        read_exel_logger.info("Файл успешно прочитан")
        return dict_read_excel
    except Exception as e:
        read_exel_logger.error(f"Error: {e}", exc_info=True)
        print(type(e).__name__)
        return []
    finally:
        read_exel_logger.info("Функция чтения EXCEL-файла завершила работу")


def get_greeting(current_time: datetime) -> str:
    """Функция возвращает приветствие в зависимости от времени суток."""
    greeting_logger.info("Функция формирования строки приветствия начала работу")
    if current_time.hour < 6:
        return "Доброй ночи"
    elif 6 <= current_time.hour < 12:
        return "Доброе утро"
    elif 12 <= current_time.hour < 18:
        return "Добрый день"
    else:
        return "Добрый вечер"


def analyzes_expenses(transactions: pd.DataFrame) -> List[Dict[str, Any]]:
    """Функция возвращает общую сумму расходов и размер кэшбэка по каждой карте за указанный период."""
    analyzes_expenses_logger.info("Функция 'analyzes_expenses' начала работу")
    try:
        filtered_by_card = transactions.groupby(transactions["Номер карты"].str[-4:])
        result_df = (
            filtered_by_card.agg(
                total_spent=("Сумма операции", lambda x: round(abs(x.sum()), 2)),
                cashback=("Сумма операции", lambda x: abs(x.sum()) // 100),
            )
            .reset_index()
            .rename(columns={"Номер карты": "last_digits"})
        )
        analyzes_expenses_logger.info(
            "Возвращаем общую сумму расходов и размер кэшбэка по каждой карте" " за указанный период"
        )
        return result_df.to_dict(orient="records")
    except Exception as e:
        analyzes_expenses_logger.error(f"Error: {e}", exc_info=True)
        print(type(e).__name__)
        return []
    finally:
        analyzes_expenses_logger.info("Функция 'analyzes_expenses' завершила работу")


def get_filtered_transactions(transactions: pd.DataFrame, date_obj: datetime, start_date: datetime) -> pd.DataFrame:
    """Функция фильтрует полученный DataFrame по дате и статусу операции и принимает во внимание только расходы"""
    filtered_transactions_logger.info("Функция 'get_filtered_transactions' начала работу")
    try:
        transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], dayfirst=True).dt.normalize()
        filtered_transactions = transactions[
            (transactions["Дата операции"] >= start_date) & (transactions["Дата операции"] <= date_obj)
        ]
        filtered_by_status = filtered_transactions[
            (filtered_transactions["Статус"] == "OK") & (filtered_transactions["Сумма операции"] <= 0)
        ]
        if filtered_by_status.empty:
            filtered_transactions_logger.info("Нет расходов за выбранный период.")
            print("Нет расходов за выбранный период.")
            return pd.DataFrame()
        filtered_transactions_logger.info("Выполнили отбор транзакций за выбранный период")
        return filtered_by_status
    except Exception as e:
        filtered_transactions_logger.error(f"Error: {e}", exc_info=True)
        print(type(e).__name__)
        return pd.DataFrame()
    finally:
        filtered_transactions_logger.info("Функция 'get_filtered_transactions' завершила работу")


def top_transactions(transactions: pd.DataFrame) -> List[Dict[Any, Any]]:
    """Функция возвращает список словарей с Топ-5 транзакциями по сумме платежа."""
    top_transactions_logger.info("Функция 'top_transactions' начала работу")
    try:
        transactions["Дата операции"] = transactions["Дата операции"].dt.strftime("%d.%m.%Y")
        transactions["Сумма операции"] = abs(transactions["Сумма операции"])
        selected_transactions = transactions[["Дата операции", "Сумма операции", "Категория", "Описание"]]
        selected_transactions = selected_transactions.sort_values("Сумма операции", ascending=False)[0:5]
        selected_transactions = selected_transactions.rename(
            columns={
                "Дата операции": "date",
                "Сумма операции": "amount",
                "Категория": "category",
                "Описание": "description",
            }
        )
        top_transactions_logger.info("Возвращаем список словарей с Топ-5 транзакциями по сумме платежа.")
        return selected_transactions.to_dict(orient="records")
    except Exception as e:
        top_transactions_logger.error(f"Error: {e}", exc_info=True)
        print(type(e).__name__)
        return []
    finally:
        top_transactions_logger.info("Функция 'top_transactions' завершила работу")


def external_api_currency() -> List[Dict[str, Any]]:
    """Функция выполняет обращение к внешнему API для получения текущего курса валют."""
    external_api_currency_logger.info("Функция получения текущего курса валют начала работу")
    result_list = []
    headers = {"apikey": API_KEY}
    try:
        for i in user_currencies:
            url = f"https://api.apilayer.com/exchangerates_data/convert?to=RUB&from={i}&amount=1"
            response = requests.get(url, headers=headers)
            status_code = response.status_code
            if status_code == 200:
                result = {"currency": i, "rate": round(response.json()["info"]["rate"], 2)}
                result_list.append(result)
            else:
                external_api_currency_logger.info(
                    f"Код статуса ответа на запрос для получения текущего курса валют " f"{status_code}"
                )
        return result_list
    except requests.exceptions.RequestException as e:
        external_api_currency_logger.error(f"Запрос для получения текущего курса валют завершился ошибкой: {str(e)}")
        print(f"Запрос для получения текущего курса валют завершился ошибкой: {str(e)}")
        return []
    finally:
        external_api_currency_logger.info("Функция получения текущего курса валют завершила работу")


def external_api_stock() -> List[Dict[str, Any]]:
    """Функция выполняет обращение к внешнему API для получения цен на акции"""
    external_api_stock_logger.info("Функция получения цен на акции начала работу")
    result_list = []
    end_date = datetime.now().date() - timedelta(days=1)
    start_date = end_date - timedelta(days=2)
    headers = {"apikey": API}
    try:
        for i in user_stocks:
            url = f"https://api.polygon.io/v2/aggs/ticker/{i}/range/1/day/{start_date}/{end_date}?apiKey={API}"
            response = requests.get(url, headers=headers)
            status_code = response.status_code
            if status_code == 200:
                result = {"stock": i, "price": round(response.json()["results"][0]["c"], 2)}
                result_list.append(result)
            else:
                external_api_stock_logger.info(
                    f"Код статуса ответа на запрос для получения цен на акции {status_code}"
                )
        return result_list
    except requests.exceptions.RequestException as e:
        external_api_stock_logger.error(f"Запрос для получения цен на акции завершился ошибкой: {str(e)}")
        print(f"Запрос для получения цен на акции завершился ошибкой: {str(e)}")
        return []
    finally:
        external_api_stock_logger.info("Функция получения цен на акции завершила работу")
