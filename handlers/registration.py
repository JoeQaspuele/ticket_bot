# handlers/registration.py
from aiogram.dispatcher import FSMContext
from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup

#1.1. Состояния (FSM) для регистрации

class RegistrationStates(StatesGroup):
    first_name = State()
    last_name = State()
    middle_name = State()
    city = State()
    confirm = State()
  
from messages import Messages
from keyboards import Keyboards

#1.2. Обработчик кнопки "Регистрация"

@dp.message_handler(text="Регистрация", state=None)
async def start_registration(message: types.Message):
    await message.answer(Messages.REGISTER_START)
    await RegistrationStates.first_name.set()

#1.3. Обработка ввода имени

@dp.message_handler(state=RegistrationStates.first_name)
async def process_first_name(message: types.Message, state: FSMContext):
    if not message.text.strip() or message.text.isdigit():
        await message.answer(Messages.EMPTY_FIELD)
        return
    
    await state.update_data(first_name=message.text.strip())
    await message.answer(Messages.REGISTER_LAST_NAME)
    await RegistrationStates.last_name.set()

#1.4 Обработка фамилии, отчества и города
@dp.message_handler(state=RegistrationStates.last_name)
async def process_last_name(message: types.Message, state: FSMContext):
    if not message.text.strip() or message.text.isdigit():
        await message.answer(Messages.EMPTY_FIELD)
        return
    
    await state.update_data(last_name=message.text.strip())
    await message.answer(Messages.REGISTER_MIDDLE_NAME)
    await RegistrationStates.middle_name.set()

@dp.message_handler(state=RegistrationStates.middle_name)
async def process_middle_name(message: types.Message, state: FSMContext):
    if not message.text.strip() or message.text.isdigit():
        await message.answer(Messages.EMPTY_FIELD)
        return
    
    await state.update_data(middle_name=message.text.strip())
    await message.answer(Messages.REGISTER_CITY)
    await RegistrationStates.city.set()

@dp.message_handler(state=RegistrationStates.city)
async def process_city(message: types.Message, state: FSMContext):
    if not message.text.strip() or message.text.isdigit():
        await message.answer(Messages.EMPTY_FIELD)
        return
    
    await state.update_data(city=message.text.strip())
    
    # Получаем все введённые данные
    user_data = await state.get_data()
    fio = f"{user_data['last_name']} {user_data['first_name']} {user_data['middle_name']}"
    
    # Получаем лимит города (из settings.py)
    from settings import CITY_LIMITS
    city_limit = CITY_LIMITS.get(user_data['city'], 0)  # Если города нет, лимит = 0
    
    await message.answer(
        Messages.REGISTER_CONFIRM(fio, user_data['city'], city_limit),
        reply_markup=Keyboards.confirm_keyboard()
    )
    await RegistrationStates.confirm.set()

#1.5. Подтверждение данных
@dp.message_handler(state=RegistrationStates.confirm)
async def process_confirm(message: types.Message, state: FSMContext):
    if message.text.lower() == 'да':
        user_data = await state.get_data()
        
        # Сохраняем в базу данных
        from database.db_operations import DBOperations
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
    
    await state.finish()


