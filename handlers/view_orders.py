from aiogram import types, Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from settings import ADMIN_IDS
from database import get_last_ticket, get_all_tickets
from utils import format_ticket_data

# Кнопки меню просмотра заказов
def get_orders_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("📄 Последний заказ"))
    kb.add(KeyboardButton("📚 Все заказы"))
    return kb

# Последний заказ пользователя
async def handle_last_order(message: types.Message):
    user_id = message.from_user.id
    ticket = await get_last_ticket(user_id)

    if ticket:
        full_name = f"{ticket.get('last_name', '')} {ticket.get('first_name', '')} {ticket.get('middle_name', '')}"
        await message.answer(format_ticket_data(ticket, full_name))
    else:
        await message.answer("У вас пока нет заказов.")

# Все заказы (только для админов)
async def handle_all_orders(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("У вас нет доступа к этой информации.")
        return

    tickets = await get_all_tickets()
    if not tickets:
        await message.answer("Заказов пока нет.")
        return

    for ticket in tickets:
        full_name = f"{ticket.get('last_name', '')} {ticket.get('first_name', '')} {ticket.get('middle_name', '')}"
        await message.answer(format_ticket_data(ticket, full_name))

# Регистрируем хендлеры
def register_order_handlers(dp: Dispatcher):
    dp.register_message_handler(handle_last_order, lambda msg: msg.text == "📄 Последний заказ")
    dp.register_message_handler(handle_all_orders, lambda msg: msg.text == "📚 Все заказы")
