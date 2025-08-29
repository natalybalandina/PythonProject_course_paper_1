# Курсовая работа № 1 "PythonProject_course_paper_1"
# Задание
Разработать приложение для анализа транзакций, которые находятся в Excel-файле. Приложение должно генерировать JSON-данные для веб-страниц, формировать Excel-отчеты, а также предоставлять другие сервисы.

Реализуйте на выбор минимум одну из задач в каждой категории. Задачи по категориям:

Веб-страницы:
Главная
События
Сервисы:
Выгодные категории повышенного кешбэка
Инвесткопилка
Простой поиск
Поиск по телефонным номерам
Поиск переводов физическим лицам
Отчеты:
Траты по категории
Траты по дням недели
Траты в рабочий/выходной день

# Установка:
Клонируйте репозиторий  
``` 
git clone nttps:https://github.com/natalybalandina/PythonProject_course_paper_1
```
# Зависимости
```
requires-python = ">=3.13"
dependencies = [
    "requests (>=2.32.5,<3.0.0)",
    "pandas (>=2.3.2,<3.0.0)",
    "openpyxl (>=3.1.5,<4.0.0)",
    "xlrd (>=2.0.2,<3.0.0)",
    "python-dotenv (>=1.1.1,<2.0.0)"
```
Зависимости устанавливаются ``` poetry install ```

# Конфигурация
Перед запуском проекта убедитесь, что все зависимости установлены и выполнены необходимые конфигурационные шаги

# Использование:
Точка запуска программы является модулем main.py. Программа запускается командой 
```
python main.py
```

# Функционал:
В проекте реализованы следующие модули: В модуле сервис - поиск переводов по физлицам В модуле reports - отчет трат по категориям В модуле utils - все вспомагательные функции в модуле views - функции для данных, которые выводятся на экран пользователя
* Пример выполнения кода:*
```
Доброй ночи
JSON-ответ:
{
    "expenses_cards": [
        {
            "last_digits": "1112",
            "total_spent": 46207.08,
            "cashback": 462.07
        },
        {
            "last_digits": "4556",
            "total_spent": 1780150.21,
            "cashback": 17801.5
        },
        {
            "last_digits": "5091",
            "total_spent": 17367.5,
            "cashback": 173.68
        },
        {
            "last_digits": "5441",
            "total_spent": 470854.8,
            "cashback": 4708.55
        },
        {
            "last_digits": "5507",
            "total_spent": 84000.0,
            "cashback": 840.0
        },
        {
            "last_digits": "6002",
            "total_spent": 69200.0,
            "cashback": 692.0
        },
        {
            "last_digits": "7197",
            "total_spent": 2487419.56,
            "cashback": 24874.2
        }
    ],
    "top_transactions": [
        {
            "date": "21.03.2019",
            "amount": 190044.51,
            "category": "Переводы",
            "description": "Перевод Кредитная карта. ТП 10.2 RUR"
        },
        {
            "date": "23.10.2018",
            "amount": 177506.03,
            "category": "Переводы",
            "description": "Перевод Кредитная карта. ТП 10.2 RUR"
        },
        {
            "date": "30.12.2021",
            "amount": 174000.0,
            "category": "Пополнения",
            "description": "Пополнение через Газпромбанк"
        },
        {
            "date": "23.10.2018",
            "amount": 150000.0,
            "category": "Переводы",
            "description": "Пополнение счета"
        },
        {
            "date": "30.07.2018",
            "amount": 150000.0,
            "category": "Пополнения",
            "description": "Пополнение. Перевод средств с торгового счета"    
        }
    ]
}
У вас на счету: 1000 рублей.
Ваш кешбэк за месяц: 0 рублей.
JSON со всеми транзакциями по физлицам:
[]
Расходы по категории 'Продукты' за последние 3 месяца:
[]
```


# Тестирование:
Коды в модульных пакетах src/ и test/ покрыты тестами. Для запуска тестов используем команду pytest.
```
platform win32 -- Python 3.13.3, pytest-8.4.1, pluggy-1.6.0
rootdir: C:\Users\...\PythonProject_course_paper_1
configfile: pyproject.toml
plugins: cov-6.2.1, mock-3.14.1
collected 25 items                                                           

tests\test_config.py .......                                           [ 28%]
tests\test_reports.py ....                                             [ 44%]
tests\test_services.py ....                                            [ 60%]
tests\test_utils.py .......                                            [ 88%]
tests\test_views.py ...                                                [100%]

============================ 25 passed in 5.00s =============================
```
После ввода команды `` `pytest --cov ``` получаем следующие результаты:
```

Name                     Stmts   Miss  Cover
--------------------------------------------
src\__init__.py              0      0   100%
src\config.py               43      8    81%
src\reports.py              52     15    71%
src\services.py             30      6    80%
src\utils.py               150     37    75%
src\views.py                64     19    70%
tests\__init__.py            0      0   100%
tests\test_config.py        53      1    98%
tests\test_reports.py       29      1    97%
tests\test_services.py      25      1    96%
tests\test_utils.py         46      1    98%
tests\test_views.py         40      6    85%
--------------------------------------------
TOTAL                      532     95    82%
============================ 25 passed in 4.01s ============================
```
Таким образом, коды покрыты тестами более 80% (по условиям задания).
Отчет о покрытии тестами сгенерирован в папке 'htmlcov' командой 'pytest --cov=src --cov-report=html'
```
============================ test session starts ============================
platform win32 -- Python 3.13.3, pytest-8.4.1, pluggy-1.6.0
rootdir: C:\Users\bal1n\Desktop\N_Balandina\PythonProject_course_paper_1
configfile: pyproject.toml
plugins: cov-6.2.1, mock-3.14.1
collected 25 items                                                           

tests\test_config.py .......                                           [ 28%] 
tests\test_reports.py ....                                             [ 44%] 
tests\test_services.py ....                                            [ 60%] 
tests\test_utils.py .......                                            [ 88%]
tests\test_views.py ...                                                [100%]

============================== tests coverage =============================== 
______________ coverage: platform win32, python 3.13.3-final-0 ______________ 

Coverage HTML written to dir htmlcov
============================ 25 passed in 5.18s =============================

```
