# settings.py
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN') or 'YOUR_BOT_TOKEN'
ADMIN_IDS = [int(id) for id in os.getenv('ADMIN_IDS', '').split(',') if id]

# Лимиты для городов
CITY_LIMITS = {
    'Москва': 25000,
    'Санкт-Петербург': 22000,
    'Уфа': 18000,
    # Добавьте другие города по необходимости
}

DB_NAME = 'tickets_bot.db'
