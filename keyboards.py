# keyboards.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from messages import Messages

class Keyboards:
    @staticmethod
    def main_menu(is_registered: bool, is_admin: bool = False):
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        if not is_registered:
            markup.add(KeyboardButton("Регистрация"))
            return markup
        
        markup.row(
            KeyboardButton("Заказать билет"),
            KeyboardButton("Заказать гостиницу")
        )
        markup.row(
            KeyboardButton("Просмотреть заказанный билет")
        )
        
        if is_admin:
            markup.add(KeyboardButton("Просмотреть все заказанные билеты"))
            
        return markup
    
    @staticmethod
    def confirm_keyboard():
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(
            KeyboardButton("Да"),
            KeyboardButton("Нет")
        )
        return markup
    
    @staticmethod
    def ticket_type_keyboard():
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(
            KeyboardButton("Авиабилет ✈️"),
            KeyboardButton("Авиабилет с пересадкой ✈️↔️✈️")
        )
        markup.row(
            KeyboardButton("Ж/Д билет 🚆"),
            KeyboardButton("Ж/Д билет с пересадкой 🚆↔️🚆")
        )
        markup.add(KeyboardButton("Отмена"))
        return markup
    
    @staticmethod
    def baggage_keyboard():
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(
            KeyboardButton("С багажом 🧳"),
            KeyboardButton("Без багажа")
        )
        markup.add(KeyboardButton("Отмена"))
        return markup
