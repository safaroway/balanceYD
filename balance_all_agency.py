import requests
import json
import random
from datetime import datetime, timedelta
from time import sleep

def process_agency_clients(token):
    clients_info = []

    # Заголовки для запросов
    headers = {
        "Authorization": "Bearer " + token,
        "Accept-Language": "ru",
        "skipReportHeader": "true",
        "skipColumnHeader": "true",
        "skipReportSummary": "true",
        "returnMoneyInMicros": "false"
    }

    # URL-адреса API
    AgencyClientsURL = 'https://api.direct.yandex.com/json/v5/agencyclients'
    BalanceURL = 'https://api.direct.yandex.ru/live/v4/json/'
    ReportsURL = 'https://api.direct.yandex.com/json/v5/reports'

    # Запрос к сервису AgencyClients
    AgencyClientsBody = {
        "method": "get",
        "params": {
            "SelectionCriteria": {"Archived": "NO"},
            "FieldNames": ["Login", "ClientInfo"],
            "Page": {"Limit": 10000, "Offset": 0}
        }
    }

    # Получение списка клиентов
    ClientList = []
    HasAllClientLoginsReceived = False

    while not HasAllClientLoginsReceived:
        ClientsResult = requests.post(AgencyClientsURL, json.dumps(AgencyClientsBody), headers=headers).json()
        for client_data in ClientsResult['result']['Clients']:
            ClientList.append(client_data)
        if ClientsResult['result'].get("LimitedBy", False):
            AgencyClientsBody['Page']['Offset'] = ClientsResult['result']["LimitedBy"]
        else:
            HasAllClientLoginsReceived = True

    # Дата начала и окончания для отчетов
    dateS = datetime.now() - timedelta(days=8)
    dateE = datetime.now() - timedelta(days=1)

    # Запрос баланса и статистики расходов для каждого клиента
    for client in ClientList:
        login = client["Login"]
        client_info = client["ClientInfo"]

        # Запрос баланса
        balance_body = {
            "method": "AccountManagement",
            "token": token,
            "locale": "ru",
            "param": {
                "Action": "Get",
                "SelectionCriteria": {"Logins": [login]}
            }
        }
        balance_response = requests.post(BalanceURL, json=balance_body)
        balance_data = balance_response.json()

        # Проверка наличия данных о балансе
        if 'Accounts' in balance_data['data'] and balance_data['data']['Accounts']:
            balance_json = balance_data['data']['Accounts'][0]
            balance = round(float(balance_json["Amount"]), 2)
        else:
            continue

        # Запрос статистики расходов
        report_headers = headers.copy()
        report_headers["Client-Login"] = login
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

        # Получение и обработка данных отчета
        report_data = ""
        while True:
            response = requests.post(ReportsURL, headers=report_headers, json=report_body)
            if response.status_code == 200:
                report_data = response.text
                break
            elif response.status_code in [201, 202]:
                sleep(2)
            else:
                break

        report_data_formatted = report_data.strip()
        if not report_data_formatted or not report_data_formatted.replace('.', '', 1).isdigit():
            report_data_formatted = "0"

        # Формирование информации о клиенте
        if balance <= 0:
            client_info_string = f'{client_info} - Деньги закончились'
        elif float(report_data_formatted) == 0:
            client_info_string = f'{client_info}: Баланс - {balance}₽. Расходов нет'
        else:
            average_daily_spend = float(report_data_formatted) / 7
            days_remaining = balance / average_daily_spend
            days_remaining_info = f"Денег хватит на {days_remaining:.2f} дней."
            client_info_string = f'{client_info}: Баланс - {balance}₽. Расход за 7 дней - {report_data_formatted}₽. {days_remaining_info}'

        clients_info.append(client_info_string)

    return clients_info

# Токены для разных агентств
token_agency_1 = 'y0_AgAAAAA2LZCOAAjHbQAAAADgXzNmMrHHkBuaQVSGVQLqG72g0Z_IfIw'
token_agency_2 = 'y0_AgAAAABl7E-XAAjHbQAAAADhcatO3Ak85rsRSfqNL97BWOyBKpXsPoE'

# Обработка клиентов первого и второго агентств
clients_info_agency_1 = process_agency_clients(token_agency_1)
clients_info_agency_2 = process_agency_clients(token_agency_2)

# Объединение и вывод информации
all_clients_info = clients_info_agency_1 + clients_info_agency_2
print("\n".join(all_clients_info))
