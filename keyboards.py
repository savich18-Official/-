from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

button_1 = KeyboardButton('/low')
button_2 = KeyboardButton('/hight')
button_3 = KeyboardButton('/custom')
button_4 = KeyboardButton('/history')

keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

keyboard.row(button_1, button_2).row(button_3, button_4)

inline_keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton('Отмена', callback_data='cancel'))
