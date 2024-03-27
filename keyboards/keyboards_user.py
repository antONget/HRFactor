from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

import logging


def keyboard_start() -> None:
    logging.info("keyboard_start")
    button_1 = InlineKeyboardButton(text='Да, хочу',  callback_data=f'yes_1')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1]],
    )
    return keyboard


def keyboards_get_phone():
    logging.info("keyboards_get_phone")
    button_1 = KeyboardButton(text='Поделиться', request_contact=True)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_1]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def keyboard_yes_2() -> None:
    logging.info("keyboard_yes_2")
    button_1 = InlineKeyboardButton(text='Да, хочу',  callback_data=f'yes_2')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1]],
    )
    return keyboard


def keyboard_url_channel() -> None:
    logging.info("keyboard_url_channel")
    button_1 = InlineKeyboardButton(text='Подписаться на канал',  url='https://t.me/hrfactor')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1]],
    )
    return keyboard