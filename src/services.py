import json
import logging
import os
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path_log_file = os.path.join(base_dir, "logs", "services.log")

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(path_log_file, "w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


def analyze_cashback_categories(data_list: List[Dict[str, Any]], year: int, month: int) -> str | None:
    """Анализирует, какие категории были наиболее выгодными для выбора в качестве категорий повышенного кешбэка.
    Входные данные: данные с транзакциями, год и месяц, за которые проводится анализ.
    На выходе — JSON с анализом, сколько на каждой категории можно заработать кешбэка в указанном месяце года."""
    cashback_analysis = defaultdict(float)
    try:
        logger.info(f"Функция {__name__} начала работу")
        for transaction in data_list:
            date_obj = datetime.strptime(transaction["Дата операции"], "%d.%m.%Y %H:%M:%S")
            if date_obj:
                year_str = date_obj.year
                month_str = date_obj.month
                if year_str == year and month_str == month:
                    category = transaction.get("Категория", "Неизвестная категория")
                    cashback_analysis[category] += transaction["Кэшбэк"]
        cashback_analysis_dict = dict(cashback_analysis)
        cashback_analysis_dict = {k: v for k, v in cashback_analysis_dict.items() if v > 0}
        if cashback_analysis_dict:
            logger.info("Выполнили отбор транзакций за выбранный период")
            cashback_analysis_int = {k: int(v) for k, v in cashback_analysis_dict.items()}
            result_cashback_analysis = dict(sorted(cashback_analysis_int.items(), key=lambda x: x[1], reverse=True))
            result_diction = json.dumps(result_cashback_analysis, ensure_ascii=False, indent=4)
            print(result_diction)
            return result_diction
        else:
            logger.info("За выбранный период нет транзакций с ненулевым кэшбэком")
            print("За выбранный период нет транзакций с ненулевым кэшбэком")
            return None
    except Exception as e:
        print(type(e).__name__)
        logger.error(f"Возникла ошибка {e}", exc_info=True)
        return None
    finally:
        logger.info(f"Функция {__name__} завершила работу")


# if __name__ == "__main__":
# transactions = [{'Дата операции': '31.12.2021 16:44:00', 'Дата платежа': '31.12.2021', 'Номер карты': '*7197',
#                      'Статус': 'OK', 'Сумма операции': -160.89, 'Валюта операции': 'RUB', 'Сумма платежа': -160.89,
#                      'Валюта платежа': 'RUB', 'Кэшбэк': 0, 'Категория': 'Супермаркеты', 'MCC': 5411.0,
#                      'Описание': 'Колхоз', 'Бонусы (включая кэшбэк)': 3, 'Округление на инвесткопилку': 0,
#                      'Сумма операции с округлением': 160.89},
#                     {'Дата операции': '31.12.2021 16:42:04', 'Дата платежа': 0, 'Номер карты': '*7197',
#                      'Статус': 'OK', 'Сумма операции': -64.0, 'Валюта операции': 'RUB', 'Сумма платежа': -64.0,
#                      'Валюта платежа': 'RUB', 'Кэшбэк': 70, 'Категория': 'Ж/д билеты', 'MCC': 5411.0,
#                      'Описание': 'Колхоз', 'Бонусы (включая кэшбэк)': 1, 'Округление на инвесткопилку': 0,
#                      'Сумма операции с округлением': 64.0}]
