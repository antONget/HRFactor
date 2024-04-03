from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state

from keyboards.keyboards_user import keyboard_start, keyboards_get_phone, keyboard_yes_2, keyboard_url_channel

from services.googlesheets import append_contact
import logging
import re
from config_data.config import Config, load_config

router = Router()
# Загружаем конфиг в переменную config
config: Config = load_config()


class User(StatesGroup):
    name_company = State()
    name_user = State()
    phone_user = State()
    friend_name = State()
    friend_phone = State()

user_dict = {}


def validate_russian_phone_number(phone_number):
    # Паттерн для российских номеров телефона
    # Российские номера могут начинаться с +7, 8, или без кода страны
    pattern = re.compile(r'^(\+7|8|7)?(\d{10})$')

    # Проверка соответствия паттерну
    match = pattern.match(phone_number)

    return bool(match)

# запуск бота пользователем /start
@router.message(CommandStart())
async def process_start_command(message: Message) -> None:
    """
    Нажатие или ввод команды /start пользователем
    :param message:
    :param state:
    :return:
    """
    logging.info(f'process_start_command: {message.chat.id}')
    await message.answer(text=f'Добрый день!\n'
                              f'<b>Я бот рекрутингового агентства HR-factor!</b>\n'
                              f'Хотите получить подарки?',
                         reply_markup=keyboard_start(),
                         parse_mode='html')


@router.callback_query(F.data == 'yes_1')
async def process_press_yes_1(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Нажатие кнопки "Да, хочу"
    :param callback:
    :param bot:
    :return:
    """
    logging.info(f'process_press_yes_1: {callback.message.chat.id}')
    await callback.message.answer(text=f'Отлично!\n'
                                       f'Напишите, пожалуйста, название вашей компании или бренда.\n\n'
                                       f'В случае отсутствия такового, укажите сферу вашей деятельности.')
    await state.set_state(User.name_company)

@router.message(F.text, StateFilter(User.name_company))
async def get_name_company(message: Message, state: FSMContext) -> None:
    """
    Обработка ввода пользователем названия компании
    :param message:
    :param state:
    :return:
    """
    logging.info(f'get_name_company: {message.chat.id}')
    await state.update_data(name_company=message.text)
    await message.answer(text='Спасибо!\n'
                              'Теперь укажите ваши ФИО.')
    await state.set_state(User.name_user)


@router.message(F.text, StateFilter(User.name_user))
async def get_name_user(message: Message, state: FSMContext) -> None:
    """
    Обработка ввода пользователем ФИО
    :param message:
    :param state:
    :return:
    """
    logging.info(f'get_name_user: {message.chat.id}')
    await state.update_data(name_user=message.text)
    await message.answer(text='Супер!\n'
                              'Напишите контактный номер телефона, по которому с вами можно связаться.',
                         reply_markup=keyboards_get_phone())
    await state.set_state(User.phone_user)


@router.message(StateFilter(User.phone_user))
async def get_phone_user(message: Message, state: FSMContext) -> None:
    """
    Получение номера телефона пользователя
    :param message:
    :param state:
    :return:
    """
    logging.info(f'get_phone_user: {message.chat.id}')
    if message.contact:
        phone = str(message.contact.phone_number)
    else:
        phone = message.text
        if not validate_russian_phone_number(phone):
            await message.answer(text="Неверный формат номера, повторите ввод.")
            return
    await state.update_data(phone_user=phone)
    await message.answer(text='Спасибо!\n'
                              'Ваш первый подарок \n'
                              '<a href="https://docs.google.com/document/d/1qhig8Sf3m7YIKvR7XiKNkuCm1IbyMx1P/edit?usp=drivesdk&ouid=101031225042222203205&rtpof=true&sd=true">«Главный файл должности собственника»</a>',
                         parse_mode='html')
    await message.answer(text='Хотите получить второй подарок: пошаговую инструкцию быстрого выхода из операционки?',
                         reply_markup=keyboard_yes_2())
    user_dict[message.chat.id] = await state.get_data()
    append_contact(list_contact=[user_dict[message.chat.id]['name_company'],
                                 user_dict[message.chat.id]['name_user'],
                                 user_dict[message.chat.id]['phone_user']],
                   sheet='contact')
    await state.set_state(default_state)

@router.callback_query(F.data == 'yes_2')
async def process_press_yes_2(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Нажатие кнопки получения второго подарка
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_press_yes_2: {callback.message.chat.id}')
    await callback.message.answer(text='Супер!\n'
                                       'Напишите контакты, кому вы хотели бы нас порекомендовать для подбора персонала.\n\n'
                                       'Для начала пришлите ФИО:')
    await state.set_state(User.friend_name)


@router.message(F.text, StateFilter(User.friend_name))
async def get_friend(message: Message, state: FSMContext) -> None:
    """
    Получаем данные о рекомендациях
    :param message:
    :param state:
    :return:
    """
    logging.info(f'get_friend: {message.chat.id}')
    await state.update_data(friend_name=message.text)
    await message.answer(text='Отлично!\n'
                              'Теперь пришлите телефон:')
    await state.set_state(User.friend_phone)


@router.message(StateFilter(User.friend_phone))
async def get_phone_friend(message: Message, state: FSMContext) -> None:
    """
    Получение номера телефона друга
    :param message:
    :param state:
    :return:
    """
    logging.info(f'get_phone_user: {message.chat.id}')
    if message.contact:
        phone = str(message.contact.phone_number)
    else:
        phone = message.text
        if not validate_russian_phone_number(phone):
            await message.answer(text="Неверный формат номера, повторите ввод.")
            return
    await state.update_data(friend_phone=phone)
    await message.answer(text='Спасибо!\n'
                              'Ваш второй подарок чек-лист \n<a href="https://drive.google.com/file/d/1W9MxscFaF7e_DQQWchKj5LrT_F5K4j0L/view">'
                              '«Как быстро выйти из операционки»</a>',
                         parse_mode='html')
    user_dict[message.chat.id] = await state.get_data()
    append_contact(list_contact=[user_dict[message.chat.id]['friend_name'],
                                 user_dict[message.chat.id]['friend_phone']],
                   sheet='friends')
    await message.answer(text='Подписвайтесь на наш телеграм канал - https://t.me/hrfactor\n\n'
                              '<b>Желаем успехов и побед в новых начинаниях!</b>',
                         reply_markup=keyboard_url_channel(),
                         parse_mode='html')
