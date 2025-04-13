
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove
from settings import CITY_LIMITS
import aiosqlite

class RegStates(StatesGroup):
    first_name = State()
    last_name = State()
    middle_name = State()
    base_city = State()
    confirm = State()

async def start_register(message: types.Message):
    await message.answer("Введите ваше имя:")
    await RegStates.first_name.set()

async def first_name_handler(message: types.Message, state: FSMContext):
    if not message.text.strip().isalpha():
        return await message.answer("Имя не должно быть пустым или содержать цифры.")
    await state.update_data(first_name=message.text.strip())
    await message.answer("Введите вашу фамилию:")
    await RegStates.last_name.set()

async def last_name_handler(message: types.Message, state: FSMContext):
    if not message.text.strip().isalpha():
        return await message.answer("Фамилия не должна быть пустой или содержать цифры.")
    await state.update_data(last_name=message.text.strip())
    await message.answer("Введите ваше отчество:")
    await RegStates.middle_name.set()

async def middle_name_handler(message: types.Message, state: FSMContext):
    if not message.text.strip().isalpha():
        return await message.answer("Отчество не должно быть пустым или содержать цифры.")
    await state.update_data(middle_name=message.text.strip())
    await message.answer("Введите ваш базовый город:")
    await RegStates.base_city.set()

async def base_city_handler(message: types.Message, state: FSMContext):
    city = message.text.strip()
    if city not in CITY_LIMITS:
        return await message.answer("Город не найден в списке допустимых. Уточните у администратора.")
    await state.update_data(base_city=city)

    data = await state.get_data()
    limit = CITY_LIMITS[city]

    summary = (f"{data['last_name']} {data['first_name']} {data['middle_name']}\n"
               f"Базовый город: {city}\n"
               f"Ваш лимит на проезд: {limit} рублей.")

    await message.answer(summary + "\nПодтвердите данные?", 
                         reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("✅ Подтвердить"))
    await RegStates.confirm.set()

async def confirm_handler(message: types.Message, state: FSMContext):
    if message.text == "✅ Подтвердить":
        data = await state.get_data()
        async with aiosqlite.connect("tickets_bot.db") as db:
            await db.execute('''
                INSERT OR IGNORE INTO users (telegram_id, first_name, last_name, middle_name, base_city)
                VALUES (?, ?, ?, ?, ?)
            ''', (message.from_user.id, data['first_name'], data['last_name'], data['middle_name'], data['base_city']))
            await db.commit()
        await message.answer("Вы успешно зарегистрированы!", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("Регистрация отменена.")
    await state.finish()

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_register, lambda m: m.text == "📝 Регистрация")
    dp.register_message_handler(first_name_handler, state=RegStates.first_name)
    dp.register_message_handler(last_name_handler, state=RegStates.last_name)
    dp.register_message_handler(middle_name_handler, state=RegStates.middle_name)
    dp.register_message_handler(base_city_handler, state=RegStates.base_city)
    dp.register_message_handler(confirm_handler, state=RegStates.confirm)
