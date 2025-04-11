# handlers/registration.py
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db_operations import DBOperations
from messages import Messages
from keyboards import Keyboards
import logging

# Создаем роутер для регистрации
registration_router = Router()

class RegistrationStates(StatesGroup):
    first_name = State()
    last_name = State()
    middle_name = State()
    city = State()
    confirm = State()

@registration_router.message(text="Регистрация", state=None)
async def start_registration(message: types.Message, state: FSMContext):
    await message.answer(Messages.REGISTER_START)
    await state.set_state(RegistrationStates.first_name)

@registration_router.message(state=RegistrationStates.first_name)
async def process_first_name(message: types.Message, state: FSMContext):
    if not message.text.strip() or message.text.isdigit():
        await message.answer(Messages.EMPTY_FIELD)
        return
    
    await state.update_data(first_name=message.text.strip())
    await message.answer(Messages.REGISTER_LAST_NAME)
    await state.set_state(RegistrationStates.last_name)

@registration_router.message(state=RegistrationStates.last_name)
async def process_last_name(message: types.Message, state: FSMContext):
    if not message.text.strip() or message.text.isdigit():
        await message.answer(Messages.EMPTY_FIELD)
        return
    
    await state.update_data(last_name=message.text.strip())
    await message.answer(Messages.REGISTER_MIDDLE_NAME)
    await state.set_state(RegistrationStates.middle_name)

@registration_router.message(state=RegistrationStates.middle_name)
async def process_middle_name(message: types.Message, state: FSMContext):
    if not message.text.strip() or message.text.isdigit():
        await message.answer(Messages.EMPTY_FIELD)
        return
    
    await state.update_data(middle_name=message.text.strip())
    await message.answer(Messages.REGISTER_CITY)
    await state.set_state(RegistrationStates.city)

@registration_router.message(state=RegistrationStates.city)
async def process_city(message: types.Message, state: FSMContext):
    if not message.text.strip() or message.text.isdigit():
        await message.answer(Messages.EMPTY_FIELD)
        return
    
    await state.update_data(city=message.text.strip())
    user_data = await state.get_data()
    fio = f"{user_data['last_name']} {user_data['first_name']} {user_data['middle_name']}"
    
    from settings import CITY_LIMITS
    city_limit = CITY_LIMITS.get(user_data['city'], 0)
    
    await message.answer(
        Messages.REGISTER_CONFIRM(fio, user_data['city'], city_limit),
        reply_markup=Keyboards.confirm_keyboard()
    )
    await state.set_state(RegistrationStates.confirm)

@registration_router.message(state=RegistrationStates.confirm)
async def process_confirm(message: types.Message, state: FSMContext):
    if message.text.lower() == 'да':
        user_data = await state.get_data()
        session = DBOperations.get_session()
        try:
            DBOperations.add_user(
                session,
                telegram_id=message.from_user.id,
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                middle_name=user_data['middle_name'],
                city=user_data['city']
            )
            await message.answer(
                Messages.DATA_SAVED,
                reply_markup=Keyboards.main_menu(is_registered=True)
            )
        except Exception as e:
            await message.answer("Ошибка при сохранении данных 😢")
            logging.error(f"Ошибка регистрации: {e}")
        finally:
            session.close()
    else:
        await message.answer(Messages.ACTION_CANCELLED)
    
    await state.clear()
