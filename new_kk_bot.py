import os
import subprocess
import schedule
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import ParseMode, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
import requests
import json
import random
from datetime import datetime, timedelta
import time
from time import sleep
from balance import balance_check


bot_token = '6474466927:AAHCASWQCdJ0Yg_1omdPRDsWw43LtnIpW9E'
bot = Bot(token=bot_token)
dp = Dispatcher(bot)

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

async def start(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Проверить расходы")).add(
        KeyboardButton("Баланс"))
    keyboard.add(KeyboardButton("Отчеты Datalens"))  # Добавление кнопки "Отчеты Datalens"
    keyboard.add(KeyboardButton("Полезные материалы"))  # Добавление кнопки "Отчеты Datalens"
    await message.answer("Просто нажми на кнопку", reply_markup=keyboard)

@dp.message_handler(Command("start"))
async def start_command(message: types.Message):
    await start(message)

@dp.message_handler(text="Баланс")
async def balance_command(message: types.Message):

    # Отправляем пользователю сообщение о том, что операция может занять время
    info_message = await message.answer("Это может занять некоторое время. Пожалуйста, подождите...")

    # Токены для разных агентств
    token_agency_1 = 'y0_AgAAAAA2LZCOAAjHbQAAAADgXzNmMrHHkBuaQVSGVQLqG72g0Z_IfIw'
    token_agency_2 = 'y0_AgAAAABl7E-XAAjHbQAAAADhcatO3Ak85rsRSfqNL97BWOyBKpXsPoE'

    # Обработка клиентов первого и второго агентств
    clients_info_agency_1 = process_agency_clients(token_agency_1)
    clients_info_agency_2 = process_agency_clients(token_agency_2)

    # Объединение и вывод информации
    all_clients_info = clients_info_agency_1 + clients_info_agency_2

    # Отправляем результат пользователю
    await message.answer("\n".join(all_clients_info), parse_mode=ParseMode.HTML)

    # Удаляем информационное сообщение о выполнении операции
    await asyncio.sleep(3)  # Можно добавить небольшую паузу перед удалением сообщения (опционально)
    await info_message.delete()

send_message_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'

chat_ids = ['376565633', '726788565', '149135354']


@dp.message_handler(lambda message: message.from_user.id == ALLOWED_USER_ID)
async def send_message_to_subscribers(message: types.Message):
    # Получаем текст сообщения для отправки
    message_text = message.text

    # Получаем текущую дату и время
    current_datetime = message.date.strftime('%Y-%m-%d %H:%M:%S')

    # Получаем имя пользователя (username) отправителя
    username = message.from_user.username

    # Форматируем текст сообщения с датой, временем и username
    formatted_message = f'[{current_datetime}] @{username}: {message_text}'

    # Сохраняем сообщение в файл "history.txt"
    with open("history.txt", "a") as file:
        file.write(formatted_message + "\n")

    # Отправляем сообщение подписчикам
    for chat_id in chat_ids:
        payload = {
            'chat_id': chat_id,
            'text': message_text
        }

        response = requests.post(send_message_url, json=payload)
        if response.status_code == 200:
            print(f'Сообщение успешно отправлено в чат {chat_id}')
        else:
            print(f'Ошибка при отправке сообщения в чат {chat_id}:', response.text)

    await message.reply("Сообщение успешно отправлено подписчикам.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)