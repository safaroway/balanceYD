import os
import subprocess
import schedule
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import ParseMode, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import json
import random
from datetime import datetime, timedelta
import time
from time import sleep
from balance import balance_check

# Входные данные
AgencyClientsURL = 'https://api.direct.yandex.com/json/v5/agencyclients'
BalanceURL = 'https://api.direct.yandex.ru/live/v4/json/'
ReportsURL = 'https://api.direct.yandex.com/json/v5/reports'
token = 'y0_AgAAAABetOqeAAjHbQAAAADgRQWkHGAKy-MnTbSiGZUzdlZdupsIyts'

# Заголовки для запросов
headers = {
    "Authorization": "Bearer " + token,
    "Accept-Language": "ru"
}

bot_token = '6474466927:AAHCASWQCdJ0Yg_1omdPRDsWw43LtnIpW9E'
bot = Bot(token=bot_token)
dp = Dispatcher(bot)
async def start(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Проверить расходы")).add(
        KeyboardButton("Баланс"))
    keyboard.add(KeyboardButton("Отчеты Datalens"))  # Добавление кнопки "Отчеты Datalens"
    keyboard.add(KeyboardButton("Полезные материалы"))  # Добавление кнопки "Отчеты Datalens"
    await message.answer("Просто нажми на кнопку", reply_markup=keyboard)

@dp.message_handler(Command("start"))
async def start_command(message: types.Message):
    # Получаем user_id и имя пользователя
    user_id = message.from_user.id
    username = message.from_user.username

@dp.message_handler(text="Баланс")
async def balance_command(message: types.Message):
    # Получаем user_id и имя пользователя
    user_id = message.from_user.id
    username = message.from_user.username

    # Отправляем пользователю сообщение о том, что операция может занять время
    info_message = await message.answer("Это может занять некоторое время. Пожалуйста, подождите...")

    # Записываем данные пользователя, если это новый пользователь
    with open(user_data_file, 'r') as file:
        existing_users = file.read()
        if f'user_id: {user_id}, username: {username}' not in existing_users:
            save_user_data(user_id, username)


    # Вставьте сюда код для работы с балансом в Google Sheets
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('custom-curve-330216-40ae6013a31d.json', scope)

    # Авторизуемся и открываем таблицу
    gc = gspread.authorize(credentials)
    spreadsheet = gc.open('Баланс KK')
    worksheet = spreadsheet.worksheet('schedule')

    # Вставляем формулу в ячейки
    worksheet.update('B2', '')
    worksheet.update('B2', 'y0_AgAAAAA2LZCOAAjHbQAAAADgXzNmMrHHkBuaQVSGVQLqG72g0Z_IfIw')
    worksheet.update('B3', '')
    worksheet.update('B3', 'y0_AgAAAAA2LZCOAAjHbQAAAADgXzNmMrHHkBuaQVSGVQLqG72g0Z_IfIw')
    worksheet.update('B4', '')
    worksheet.update('B4', 'y0_AgAAAAA2LZCOAAjHbQAAAADgXzNmMrHHkBuaQVSGVQLqG72g0Z_IfIw')
    worksheet.update('B5', '')
    worksheet.update('B5', 'y0_AgAAAAA2LZCOAAjHbQAAAADgXzNmMrHHkBuaQVSGVQLqG72g0Z_IfIw')
    worksheet.update('B6', '')
    worksheet.update('B6', 'y0_AgAAAAA2LZCOAAjHbQAAAADgXzNmMrHHkBuaQVSGVQLqG72g0Z_IfIw')
    worksheet.update('B7', '')
    worksheet.update('B7', 'y0_AgAAAAA2LZCOAAjHbQAAAADgXzNmMrHHkBuaQVSGVQLqG72g0Z_IfIw')
    worksheet.update('B8', '')
    worksheet.update('B8', 'y0_AgAAAAA2LZCOAAjHbQAAAADgXzNmMrHHkBuaQVSGVQLqG72g0Z_IfIw')
    worksheet.update('B9', '')
    worksheet.update('B9', 'y0_AgAAAAA2LZCOAAjHbQAAAADgXzNmMrHHkBuaQVSGVQLqG72g0Z_IfIw')
    worksheet.update('B10', '')
    worksheet.update('B10', 'y0_AgAAAAA2LZCOAAjHbQAAAADgXzNmMrHHkBuaQVSGVQLqG72g0Z_IfIw')
    worksheet.update('B11', '')
    worksheet.update('B11', 'y0_AgAAAAA2LZCOAAjHbQAAAADgXzNmMrHHkBuaQVSGVQLqG72g0Z_IfIw')
    worksheet.update('B12', '')
    worksheet.update('B12', 'y0_AgAAAABl7E-XAAjHbQAAAADhcatO3Ak85rsRSfqNL97BWOyBKpXsPoE')
    worksheet.update('B13', '')
    worksheet.update('B13', 'y0_AgAAAAA2LZCOAAjHbQAAAADgXzNmMrHHkBuaQVSGVQLqG72g0Z_IfIw')
    worksheet.update('B14', '')
    worksheet.update('B14', 'y0_AgAAAAA2LZCOAAjHbQAAAADgXzNmMrHHkBuaQVSGVQLqG72g0Z_IfIw')
    worksheet.update('B15', '')
    worksheet.update('B15', 'y0_AgAAAAA2LZCOAAjHbQAAAADgXzNmMrHHkBuaQVSGVQLqG72g0Z_IfIw')
    worksheet.update('B16', '')
    worksheet.update('B16', 'y0_AgAAAABl7E-XAAjHbQAAAADhcatO3Ak85rsRSfqNL97BWOyBKpXsPoE')
    worksheet.update('B17', '')
    worksheet.update('B17', 'y0_AgAAAAA2LZCOAAjHbQAAAADgXzNmMrHHkBuaQVSGVQLqG72g0Z_IfIw')
    worksheet.update('B18', '')
    worksheet.update('B18', 'y0_AgAAAAA2LZCOAAjHbQAAAADgXzNmMrHHkBuaQVSGVQLqG72g0Z_IfIw')
    worksheet.update('B19', '')
    worksheet.update('B19', 'y0_AgAAAABl7E-XAAjHbQAAAADhcatO3Ak85rsRSfqNL97BWOyBKpXsPoE')
    worksheet.update('B20', '')
    worksheet.update('B20', 'y0_AgAAAABl7E-XAAjHbQAAAADhcatO3Ak85rsRSfqNL97BWOyBKpXsPoE')
    worksheet.update('B21', '')
    worksheet.update('B21', 'y0_AgAAAABl7E-XAAjHbQAAAADhcatO3Ak85rsRSfqNL97BWOyBKpXsPoE')

    # Получаем значения ячеек в столбце J, начиная со второй строки
    values = worksheet.col_values(10)[1:]

    response = "\n"
    for value in values:
        message_text = value.strip()  # Удаляем лишние пробелы по краям значения
        if "баланс" in message_text.lower():  # Проверяем, содержит ли строка слово "баланс"
            response += f"<b>{message_text.split(':')[0]}</b>: {message_text.split(':')[1]}\n"

    await message.answer(response, parse_mode=ParseMode.HTML)

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