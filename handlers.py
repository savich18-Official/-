import logging
import re
from typing import Tuple, Union

from aiogram import types
from aiogram.dispatcher import FSMContext, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
import aiogram.utils.markdown as fmt
from sqlite3 import IntegrityError
from telegram_bot_pagination import InlineKeyboardPaginator

from create_bot import bot
from keyboards import keyboard, inline_keyboard
from API import request_data
import db

flag = False
data = dict()


class FSM(StatesGroup):
    """Класс состояний"""
    type_number = State()
    number_positions = State()
    search_range = State()


async def start(message: types.Message) -> None:
    """Хенделер срабатывающий на команды /start /help c выводом клавиатуры"""

    try:
        db.add_user(message.from_user.id)
    except IntegrityError as ex:
        logging.error('{ex}: Данный пользователь уже есть в базе данных'.format(ex=ex))

    await message.answer('Привет {user_name}!\nЯ бот, позволяющий осуществлять поиск и сортировку по фильмам!\
                         \nВведи нужную команду и начнем!'.format(user_name=message.from_user.first_name),
                         reply_markup=keyboard)


async def low(message: types.Message) -> None:
    """
    Хенделер срабатывающий на команду /low и запускающий машину состояний для отображения категорий в порядке
    возрастания
    """
    await FSM.type_number.set()
    db.add_info('command', "'low'", message.from_user.id)
    db.add_info('sort_type', '1', message.from_user.id)
    await message.answer('Пожалуйста введите категорию по которой необходимо произвести поиск \
                        \n(1 - фильмы | 2 - ТВ-сериалы | 3 - мультфильмы | 4 - аниме | 5 - мультсериалы | 6 - ТВ-шоу)',\
                         reply_markup=inline_keyboard)


async def cancel_handlers(message: types.Message, state: FSMContext) -> None:
    """Хенделер срабатывающий на команду /cancel или сообщение "отмена". Прерывает работу машины состояний"""
    cur_state = await state.get_state()
    if cur_state is None:
        return
    global flag
    flag = False
    await state.finish()
    await message.reply('Команда отменена')


async def cancel_call(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Хенделер срабатывающий на нажатие инлайн кнопки "отмена". Прерывает работу машины состояний"""
    cur_state = await state.get_state()
    if cur_state is None:
        return
    await state.finish()
    global flag
    flag = False
    await callback.message.reply('Команда отменена')
    await callback.answer()


async def save_type_number(message: types.Message, state: FSMContext) -> None:
    """Хенделер записывающий результат выбора категории и переключающий машину состаяний на следующий шаг"""
    if message.text in ('1', '2', '3', '4', '5', '6'):
        db.add_info('type_number', message.text, message.from_user.id)
        db.add_info('page', '1', message.from_user.id)
        await FSM.next()
        await message.reply('Категория успешно выбрана\nВведите количество отображений (не больше 300)', \
                            reply_markup=inline_keyboard)
    else:
        await message.reply('Что-то пошло не так :(\nПопробуйте еще раз!', reply_markup=inline_keyboard)


async def save_number(message: types.Message, state: FSMContext) -> None:
    """
    Хенделер записывающий количество объектов выбранной категории
    """
    if message.text.isdigit():
        if int(message.text) > 300:
            await message.reply('Количество отображений не может превышать 300!\
                                \nВыставлено максимальное количество отображений!')
            num = 300
        else:
            num = message.text
        db.add_info('limit_request', num, message.from_user.id)
        db.add_info('search_range', '"1-10"', message.from_user.id)
        global flag
        if not flag:
            await state.finish()
            result = db.result(message.from_user.id)
            await answer_result(result, message)
        else:
            flag = False
            await FSM.next()
            await message.reply('Количество успешно выбрано\nВведите диапазон (от 0 до 10 через дефис)',\
                                reply_markup=inline_keyboard)
    else:
        await message.reply('Что-то пошло не так :(\nПопробуйте еще раз!', reply_markup=inline_keyboard)


async def save_search_range(message: types.Message, state: FSMContext) -> None:
    """
    Хенделер записывающий диапазон критерия сортировки выбранной категории
    """
    pattern = r'[0-9]+[-][0-9]+'
    if re.search(pattern, message.text.replace(' ', '')) or message.text.isdigit():
        if all((lambda num: float(num) < 10, message.text.replace(' ', '').split('-'))):
            db.add_info('search_range', f"'{message.text.replace(' ', '')}'", message.from_user.id)
            await state.finish()
            result = db.result(message.from_user.id)
            await answer_result(result, message)
    else:
        await message.reply('Что-то пошло не так :(\nПопробуйте еще раз!', reply_markup=inline_keyboard)


async def answer_result(result: Union[Tuple, None], message: Union[types.Message, types.CallbackQuery],
                        index: int = 1) -> None:
    """
    Асинхроная функция отправляющая результат пользователю
    """
    if isinstance(message, types.Message):
        db.add_request(result)
        global data
        data = await request_data(result)

        text = 'Текущее содержание словаря data:'
        for key in data.keys():
            text = '\n'.join([text, f'{key}: {len(data[key])}'])
        logging.info(text)

    catalog = data[message.from_user.id]

    if len(catalog) > 0:
        pages_inline_keyboard = InlineKeyboardPaginator(len(catalog),
                                                        current_page=index,
                                                        data_pattern='catalog#{page}').markup
        current_dict = catalog[index - 1]

        try:
            link = current_dict["poster"]["url"]
        except:
            link = None

        await bot.send_message(message.from_user.id, f'{fmt.hide_link(link)}Название: {current_dict["name"]}\
                               \nГод выпуска: {current_dict["year"]}\nКатегория: {current_dict["type"]}\
                               \nРейтинг КиноПоиска: {str(current_dict["rating"]["kp"])}',
                               parse_mode=types.ParseMode.HTML,
                               reply_markup=pages_inline_keyboard)

    else:
        await bot.send_message(message.from_user.id, 'Упс! Кажется ничего нет :(')


async def next_page_call(callback: types.CallbackQuery) -> None:
    """Хенделер срабатывающий при нажатии инлайн кнопки с номером страницы """
    page = int(callback.data.split('#')[1])
    result = None
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    await answer_result(result, callback, page)
    await callback.answer()


async def hight(message: types.Message) -> None:
    """
    Хенделер срабатывающий на команду /hight и запускающий машину состояний для отображения категорий в порядке
    убывания
    """
    await FSM.type_number.set()
    db.add_info('command', '"hight"', message.from_user.id)
    db.add_info('sort_type', '-1', message.from_user.id)
    await message.answer('Пожалуйста введите категорию по которой необходимо произвести поиск \
                        \n(1 - фильмы | 2 - ТВ-сериалы | 3 - мультфильмы | 4 - аниме | 5 - мультсериалы | 6 - ТВ-шоу)', \
                         reply_markup=inline_keyboard)


async def custom(message: types.Message) -> None:
    """
    Хенделер срабатывающий на команду /custom и запускающий машину состояний для отображения категорий в выбранном
    пользователем диапазоне по сортировочному ключу
    """
    global flag
    flag = True
    db.add_info('command', '"custom"', message.from_user.id)
    db.add_info('sort_type', '1', message.from_user.id)
    await FSM.type_number.set()
    await message.answer('Пожалуйста введите категорию по которой необходимо произвести поиск \
                         \n(1 - фильмы | 2 - ТВ-сериалы | 3 - мультфильмы | 4 - аниме | 5 - мультсериалы | 6 - ТВ-шоу)', \
                         reply_markup=inline_keyboard)


async def history(message: types.Message) -> None:
    """
    Хенделер срабатывающий на команду /history и выводящий краткую информацию о 10 последних запросах пользователя
    """
    pattern = '{num}) Команда: {command}; категория поиска: {type_number} количество: {limit_request}.'
    message_history = 'История запросов:'

    history_list = db.show_history(message.from_user.id)
    for num, i_history in enumerate(history_list[::-1], start=1):
        message_history = '\n'.join([message_history, pattern.format(num=num,
                                                                     command=i_history[2],
                                                                     type_number=i_history[6],
                                                                     limit_request=i_history[5])]
                                    )
    await message.reply(message_history)


def registr_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(start, commands=['start', 'help'])
    dp.register_message_handler(low, commands=['low'], state=None)
    dp.register_message_handler(hight, commands=['hight'], state=None)
    dp.register_callback_query_handler(cancel_call, Text(equals='cancel'), state='*')
    dp.register_callback_query_handler(next_page_call, Text(startswith='catalog'))
    dp.register_message_handler(cancel_handlers, commands=['cancel'], state='*')
    dp.register_message_handler(cancel_handlers, Text(equals='отмена', ignore_case=True), state='*')
    dp.register_message_handler(save_type_number, state=FSM.type_number)
    dp.register_message_handler(save_number, state=FSM.number_positions)
    dp.register_message_handler(save_search_range, state=FSM.search_range)
    dp.register_message_handler(custom, commands=['custom'], state=None)
    dp.register_message_handler(history, commands=['history'])
