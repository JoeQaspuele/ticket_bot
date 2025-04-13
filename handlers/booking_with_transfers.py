from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from datetime import datetime
from settings import CITY_LIMITS
import aiosqlite

class TransferTicketState(StatesGroup):
    transport_type = State()
    date_time = State()
    route1 = State()
    route2 = State()
    flight_info = State()
    luggage = State()
    amount = State()
    confirm = State()

async def start_transfer_booking(message: types.Message, state: FSMContext):
    await state.update_data(transport_type=message.text)
    await message.answer("Введите дату и время отправления (например: 20.04.2025 08:30):",
                         reply_markup=ReplyKeyboardRemove())
    await TransferTicketState.date_time.set()

async def transfer_date_time_handler(message: types.Message, state: FSMContext):
    try:
        date_time = datetime.strptime(message.text.strip(), "%d.%m.%Y %H:%M")
        if date_time < datetime.now():
            raise ValueError("Дата в прошлом.")
        await state.update_data(date_time=message.text.strip())
        await message.answer("Введите маршрут первого рейса (например: Уфа - Москва):")
        await TransferTicketState.route1.set()
    except Exception:
        await message.answer("Дата указана неверно или в прошлом. Попробуйте снова.")

async def transfer_route1_handler(message: types.Message, state: FSMContext):
    await state.update_data(route1=message.text.strip())
    await message.answer("Введите маршрут второго рейса (например: Москва - Красноярск):")
    await TransferTicketState.route2.set()

async def transfer_route2_handler(message: types.Message, state: FSMContext):
    await state.update_data(route2=message.text.strip())
    await message.answer("Введите номер рейса/поезда и название авиакомпании/перевозчика:")
    await TransferTicketState.flight_info.set()

async def transfer_flight_info_handler(message: types.Message, state: FSMContext):
    await state.update_data(flight_info=message.text.strip())
    data = await state.get_data()

    if "Авиабилет" in data['transport_type']:
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("С багажом", "Без багажа")
        await message.answer("Багаж включён?", reply_markup=markup)
        await TransferTicketState.luggage.set()
    else:
        await state.update_data(luggage="—")
        await ask_transfer_amount(message, state)

async def transfer_luggage_handler(message: types.Message, state: FSMContext):
    await state.update_data(luggage=message.text)
    await ask_transfer_amount(message, state)

async def ask_transfer_amount(message, state):
    await message.answer("Введите сумму билета (только цифры):", reply_markup=ReplyKeyboardRemove())
    await TransferTicketState.amount.set()

async def transfer_amount_handler(message: types.Message, state: FSMContext):
    if not message.text.strip().isdigit():
        return await message.answer("Введите только цифры.")

    amount = int(message.text.strip())
    user_id = message.from_user.id
    async with aiosqlite.connect("tickets_bot.db") as db:
        async with db.execute("SELECT base_city, last_name, first_name, middle_name FROM users WHERE telegram_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
    if not row:
        return await message.answer("Вы не зарегистрированы.")

    base_city, last, first, middle = row
    limit = CITY_LIMITS.get(base_city, 0)

    await state.update_data(amount=amount, fio=f"{last} {first} {middle}", base_city=base_city, limit=limit)

    if amount > limit:
        await message.answer("⚠️ Сумма превышает лимит! Необходимо заполнить заявление на удержание.")

    data = await state.get_data()
    summary = (
        f"{data['fio']}\n"
        f"Дата и время: {data['date_time']}\n"
        f"Маршрут 1: {data['route1']}\n"
        f"Маршрут 2: {data['route2']}\n"
        f"Рейс: {data['flight_info']}\n"
        f"Багаж: {data['luggage']}\n"
        f"Сумма: {amount} рублей."
    )

    markup = ReplyKeyboardMarkup(resize_keyboard=True).add("✅ Подтвердить", "❌ Отменить")
    await message.answer(summary + "\n\nПодтвердить заказ?", reply_markup=markup)
    await TransferTicketState.confirm.set()

async def transfer_confirm_handler(message: types.Message, state: FSMContext):
    if message.text == "✅ Подтвердить":
        data = await state.get_data()
        user_id = message.from_user.id

        async with aiosqlite.connect("tickets_bot.db") as db:
            await db.execute('''
                INSERT INTO tickets (user_id, date_time, route, flight_number, company, luggage, amount, is_transfer, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, data['date_time'], f"{data['route1']} / {data['route2']}",
                data['flight_info'], data['flight_info'], data['luggage'],
                data['amount'], 1, datetime.now().isoformat()
            ))
            await db.commit()

        await message.answer("🎉 Билет с пересадкой успешно сохранён!", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("Заказ отменён.")
    await state.finish()

def register_transfer_handlers(dp):
    dp.register_message_handler(start_transfer_booking, lambda m: m.text in ["🛫✈ Авиабилет (с пересадкой)", "🚆⛓ Ж/д билет (с пересадкой)"])
    dp.register_message_handler(transfer_date_time_handler, state=TransferTicketState.date_time)
    dp.register_message_handler(transfer_route1_handler, state=TransferTicketState.route1)
    dp.register_message_handler(transfer_route2_handler, state=TransferTicketState.route2)
    dp.register_message_handler(transfer_flight_info_handler, state=TransferTicketState.flight_info)
    dp.register_message_handler(transfer_luggage_handler, state=TransferTicketState.luggage)
    dp.register_message_handler(transfer_amount_handler, state=TransferTicketState.amount)
    dp.register_message_handler(transfer_confirm_handler, state=TransferTicketState.confirm)
