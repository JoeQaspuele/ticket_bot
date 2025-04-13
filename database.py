import aiosqlite

async def init_db():
    async with aiosqlite.connect("tickets_bot.db") as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE,
                first_name TEXT,
                last_name TEXT,
                middle_name TEXT,
                base_city TEXT
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date_time TEXT,
                route TEXT,
                route_2 TEXT,
                flight_number TEXT,
                company TEXT,
                luggage TEXT,
                amount INTEGER,
                is_transfer BOOLEAN,
                created_at TEXT
            )
        ''')
        await db.commit()
