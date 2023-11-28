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

    # Вызываем функцию balance_check для получения информации о балансе
    balance_info = balance_check()

    # Отправляем результат пользователю
    # Теперь balance_info - это список, его можно безопасно объединять в строку
    await message.answer("\n".join(balance_info), parse_mode=ParseMode.HTML)

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