# bot.py
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import settings
from database import init_db

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

async def on_startup(dp):
    await init_db()

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.answer("Привет! Добро пожаловать в бота.\nЕсли вы новый пользователь, нажмите 'Регистрация'",
                         reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("📝 Регистрация"))

if __name__ == "__main__":
    from handlers import register
    register.register_handlers(dp)
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
