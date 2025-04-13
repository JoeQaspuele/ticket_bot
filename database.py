import aiosqlite
import sqlite3


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


def get_last_order(user_id):
    conn = sqlite3.connect("tickets_bot.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC LIMIT 1",
        (user_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_orders():
    conn = sqlite3.connect("tickets_bot.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM orders ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

