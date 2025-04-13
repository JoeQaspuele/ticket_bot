from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import aiosqlite
from settings import CITY_LIMITS
from datetime import datetime

class TicketState(StatesGroup):
    transport_type = State()
    date_time = State()
    route = State()
    flight_info = State()
    luggage = State()
    amount = State()
    confirm = State()

