import requests
import json
import random
from datetime import datetime, timedelta
import time
from time import sleep

# Функция замены значений '--' на 'null'
def change_0(cell):
    if cell == '--':
        cell = 'null'
    return cell

# Входные данные
AgencyClientsURL = 'https://api.direct.yandex.com/json/v5/agencyclients'
BalanceURL = 'https://api.direct.yandex.ru/live/v4/json/'
ReportsURL = 'https://api.direct.yandex.com/json/v5/reports'
token = 'y0_AgAAAAA2LZCOAAjHbQAAAADgXzNmMrHHkBuaQVSGVQLqG72g0Z_IfIw'

# Заголовки для запросов
headers = {
    "Authorization": "Bearer " + token,
    "Accept-Language": "ru"
}


# Запрос к сервису AgencyClients
AgencyClientsBody = {
    "method": "get",
    "params": {
        "SelectionCriteria": {
            "Archived": "NO"
        },
        "FieldNames": ["Login",
                       "ClientInfo"],
        "Page": {
            "Limit": 10000,
            "Offset": 0
        }
    }
}

# Получение списка клиентов
ClientList = []
HasAllClientLoginsReceived = False

while not HasAllClientLoginsReceived:
    ClientsResult = requests.post(AgencyClientsURL, json.dumps(AgencyClientsBody), headers=headers).json()
    for client_data in ClientsResult['result']['Clients']:
        ClientList.append(client_data)  # Теперь сохраняем весь объект клиента
    if ClientsResult['result'].get("LimitedBy", False):
        AgencyClientsBody['Page']['Offset'] = ClientsResult['result']["LimitedBy"]
    else:
        HasAllClientLoginsReceived = True

# --- Подготовка запроса к сервису Reports ---
# Дополнительные HTTP-заголовки для запроса отчетов
headers['skipReportHeader'] = "true"
headers['skipColumnHeader'] = "true"
headers['skipReportSummary'] = "true"
headers['returnMoneyInMicros'] = "false"

# Дата начала (7 дней назад от текущей даты)
dateS = datetime.now() - timedelta(days=8)
# Дата окончания (вчерашняя дата)
dateE = datetime.now() - timedelta(days=1)

# Запрос баланса для каждого клиента
for client in ClientList:
    login = client["Login"]
    client_info = client["ClientInfo"]  # Добавлено извлечение ClientInfo

    # Запрос баланса
    balance_body = {
        "method": "AccountManagement",
        "token": token,
        "locale": "ru",
        "param": {
            "Action": "Get",
            "SelectionCriteria": {
                "Logins": [login]
            }
        }
    }

    balance_response = requests.post(BalanceURL, json=balance_body)
    balance_data = balance_response.json()

    # Выводим полный ответ API для отладки
    # print("Ответ API:")
    # print(json.dumps(balance_data, indent=4, ensure_ascii=False))

    # Проверяем, существует ли список 'Accounts' и содержит ли он элементы
    if 'Accounts' in balance_data['data'] and balance_data['data']['Accounts']:
        balance_json = balance_data['data']['Accounts'][0]
        balance = round(float(balance_json["Amount"]), 2)

    else:
        # Обработка случая, когда информация о счете отсутствует
        # print(f"Информация о балансе для клиента {client['ClientInfo']} не найдена.")
        continue

    # Запрос статистики расходов
    report_headers = {
        "Authorization": "Bearer " + token,
        "Accept-Language": "en",
        "processingMode": "auto",
        "returnMoneyInMicros": "false",
        "skipReportHeader": "true",
        "skipColumnHeader": "true",
        "skipReportSummary": "true",
        "Client-Login": login  # Добавление логина клиента
    }

    report_number = random.randrange(1, 200000)
    report_body = {
        "params": {
            'SelectionCriteria': {
                "DateFrom": dateS.strftime('%Y-%m-%d'),
                "DateTo": dateE.strftime('%Y-%m-%d')
            },
            "FieldNames": ["Cost"],
            "ReportName": f'Отчет №{report_number}',
            "Page": {"Limit": 10000000},
            "ReportType": "CUSTOM_REPORT",
            "DateRangeType": "CUSTOM_DATE",
            "Format": "TSV",
            "IncludeVAT": "YES"
        }
    }

    report_data = ""
    while True:
        response = requests.post(ReportsURL, headers=report_headers, json=report_body)

        if response.status_code == 200:
            report_data = response.text
            break
        elif response.status_code == 201:
            # Обработка случая, когда отчет поставлен в очередь
            #print("Отчет успешно поставлен в очередь в режиме офлайн")
            sleep(2)  # Ожидание перед повторной отправкой запроса
        elif response.status_code == 202:
            #print("Отчет формируется в режиме офлайн")
            sleep(2)  # Ожидание перед повторной отправкой запроса
        else:
            if response.text:
                try:
                    print("JSON-код ответа сервера: \n{}".format(
                        json.dumps(response.json(), indent=4, ensure_ascii=False)))
                except json.JSONDecodeError:
                    print("Ошибка декодирования JSON. Текст ответа: {}".format(response.text))
            else:
                print("Ответ сервера не содержит данных")
            break

    report_data_formatted = report_data.strip()
    if not report_data_formatted or not report_data_formatted.replace('.', '', 1).isdigit():
        report_data_formatted = "0"

    if balance <= 0:
        # Вывод только информации о клиенте, если баланс равен 0
        print(f'Клиент: {client_info} - Деньги закончились')
    elif float(report_data_formatted) == 0:
        # Вывод информации о клиенте и балансе, если расход за последние 7 дней равен 0
        print(f'Клиент: {client_info}. Баланс: {balance} руб. Расходов нет')
    else:
        # Подготовка строки с информацией о количестве дней
        average_daily_spend = float(report_data_formatted) / 7
        days_remaining = balance / average_daily_spend
        days_remaining_info = f"Денег хватит на: {days_remaining:.2f} дней."

        print(
            f'Клиент: {client_info}. Баланс: {balance} руб. Расход за 7 дней: {report_data_formatted} руб. {days_remaining_info}')