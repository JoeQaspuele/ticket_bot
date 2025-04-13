# main.py
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage  # ← Новый путь
from aiogram.fsm.context import FSMContext  # ← Новый путь
from aiogram.fsm.state import State, StatesGroup
from settings import BOT_TOKEN, ADMIN_IDS
from messages import Messages
from keyboards import Keyboards
from database.db_operations import DBOperations
from handlers.registration import registration_router
from handlers.registration import router as registration_router

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
# После создания диспетчера
dp.include_router(registration_router)



# Состояния для регистрации
class RegistrationStates(StatesGroup):
    first_name = State()
    last_name = State()
    middle_name = State()
    city = State()
    confirm = State()

# Состояния для заказа билета
class TicketStates(StatesGroup):
    ticket_type = State()
    departure_date = State()
    route = State()
    route_part1 = State()  # Для билетов с пересадкой
    route_part2 = State()  # Для билетов с пересадкой
    flight_number = State()
    baggage = State()      # Только для авиабилетов
    price = State()
    confirm = State()

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    session = DBOperations.get_session()
    try:
        user = DBOperations.get_user_by_telegram_id(session, message.from_user.id)
        
        if user:
            # Пользователь уже зарегистрирован
            is_admin = message.from_user.id in ADMIN_IDS
            await message.answer(
                Messages.WELCOME_REGISTERED,
                reply_markup=Keyboards.main_menu(is_registered=True, is_admin=is_admin)
            )
        else:
            # Новый пользователь
            await message.answer(
                Messages.WELCOME,
                reply_markup=Keyboards.main_menu(is_registered=False)
            )
    except Exception as e:
        logger.error(f"Error in cmd_start: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")
    finally:
        session.close()

# Здесь будут другие обработчики...

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
