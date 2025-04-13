from aiogram import types, Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from settings import ADMIN_IDS
from database import get_last_order, get_all_orders
from utils import format_order_data


# Кнопки меню просмотра заказов
def get_orders_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("📄 Последний заказ"))
    kb.add(KeyboardButton("📚 Все заказы"))
    return kb


# Последний заказ пользователя
async def handle_last_order(message: types.Message):
    user_id = message.from_user.id
    order = get_last_order(user_id)

    if order:
        await message.answer(format_order_data(order))
    else:
        await message.answer("У вас пока нет заказов.")


# Все заказы (только для админов)
async def handle_all_orders(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("У вас нет доступа к этой информации.")
        return

    orders = get_all_orders()
    if not orders:
        await message.answer("Заказов пока нет.")
        return

    for order in orders:
        await message.answer(format_order_data(order))


# Регистрируем хендлеры
def register_order_handlers(dp: Dispatcher):
    dp.register_message_handler(handle_last_order, lambda msg: msg.text == "📄 Последний заказ")
    dp.register_message_handler(handle_all_orders, lambda msg: msg.text == "📚 Все заказы")
