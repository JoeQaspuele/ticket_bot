
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import aiosqlite
from settings import CITY_LIMITS
from datetime import datetime, datetime as dt

class TicketState(StatesGroup):
    transport_type = State()
    date_time = State()
    route = State()
    flight_info = State()
    luggage = State()
    amount = State()
    confirm = State()

async def start_booking(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🛫 Авиабилет", "🚆 Ж/д билет")
    markup.add("🛫✈ Авиабилет (с пересадкой)", "🚆⛓ Ж/д билет (с пересадкой)")
    await message.answer("Выберите тип билета:", reply_markup=markup)
    await TicketState.transport_type.set()

async def transport_chosen(message: types.Message, state: FSMContext):
    await state.update_data(transport_type=message.text)
    await message.answer("Введите дату и время отправления (например: 20.04.2025 08:30):",
                         reply_markup=ReplyKeyboardRemove())
    await TicketState.date_time.set()

async def date_time_handler(message: types.Message, state: FSMContext):
    try:
        date_time = datetime.strptime(message.text.strip(), "%d.%m.%Y %H:%M")
        if date_time < datetime.now():
            raise ValueError("Дата в прошлом.")
        await state.update_data(date_time=message.text.strip())
        await message.answer("Введите маршрут (например: Уфа - Москва):")
        await TicketState.route.set()
    except Exception:
        await message.answer("Дата указана неверно или в прошлом. Попробуйте снова.")

async def route_handler(message: types.Message, state: FSMContext):
    await state.update_data(route=message.text.strip())
    await message.answer("Введите номер рейса/поезда и название авиакомпании/перевозчика:")
    await TicketState.flight_info.set()

async def flight_info_handler(message: types.Message, state: FSMContext):
    await state.update_data(flight_info=message.text.strip())
    data = await state.get_data()

    if "Авиабилет" in data['transport_type']:
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("С багажом", "Без багажа")
        await message.answer("Багаж включён?", reply_markup=markup)
        await TicketState.luggage.set()
    else:
        await state.update_data(luggage="—")
        await ask_amount(message, state)

async def luggage_handler(message: types.Message, state: FSMContext):
    await state.update_data(luggage=message.text)
    await ask_amount(message, state)

async def ask_amount(message, state):
    await message.answer("Введите сумму билета (только цифры):", reply_markup=ReplyKeyboardRemove())
    await TicketState.amount.set()

async def amount_handler(message: types.Message, state: FSMContext):
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
        f"{data['fio']}
"
        f"Дата и время: {data['date_time']}
"
        f"Маршрут: {data['route']}
"
        f"Рейс: {data['flight_info']}
"
        f"Багаж: {data['luggage']}
"
        f"Сумма: {amount} рублей."
    )

    markup = ReplyKeyboardMarkup(resize_keyboard=True).add("✅ Подтвердить", "❌ Отменить")
    await message.answer(summary + "\n\nПодтвердить заказ?", reply_markup=markup)
    await TicketState.confirm.set()

async def confirm_handler(message: types.Message, state: FSMContext):
    if message.text == "✅ Подтвердить":
        data = await state.get_data()
        user_id = message.from_user.id

        async with aiosqlite.connect("tickets_bot.db") as db:
            await db.execute('''
                INSERT INTO tickets (user_id, date_time, route, flight_number, company, luggage, amount, is_transfer, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, data['date_time'], data['route'], 
                data['flight_info'], data['flight_info'], 
                data['luggage'], data['amount'], 0, dt.now().isoformat()
            ))
            await db.commit()

        await message.answer("🎉 Билет успешно сохранён!", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("Заказ отменён.")
    await state.finish()

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_booking, lambda m: m.text == "📦 Заказать билет")
    dp.register_message_handler(transport_chosen, state=TicketState.transport_type)
    dp.register_message_handler(date_time_handler, state=TicketState.date_time)
    dp.register_message_handler(route_handler, state=TicketState.route)
    dp.register_message_handler(flight_info_handler, state=TicketState.flight_info)
    dp.register_message_handler(luggage_handler, state=TicketState.luggage)
    dp.register_message_handler(amount_handler, state=TicketState.amount)
    dp.register_message_handler(confirm_handler, state=TicketState.confirm)
