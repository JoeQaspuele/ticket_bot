import sqlite3

from settings import DB_NAME

def create_connection():
    """Создает соединение с базой данных."""
    conn = sqlite3.connect(DB_NAME)
    return conn

def create_tables():
    """Создает таблицы в базе данных."""
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            full_name TEXT,
            city TEXT,
            limit INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            ticket_type TEXT,
            date_time TEXT,
            route TEXT,
            route2 TEXT,
            flight_number TEXT,
            baggage TEXT,
            price REAL,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    """)

    conn.commit()
    conn.close()

def get_user(user_id):
    """Получает данные пользователя из базы данных."""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT full_name, city, limit FROM users WHERE user_id = ?", (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data

def add_user(user_id, full_name, city, limit):
    """Добавляет нового пользователя в базу данных."""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (user_id, full_name, city, limit) VALUES (?, ?, ?, ?)",
                   (user_id, full_name, city, limit))
    conn.commit()
    conn.close()

def add_ticket(user_id, ticket_type, date_time, route, route2, flight_number, baggage, price):
    """Добавляет информацию о билете в базу данных."""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tickets (user_id, ticket_type, date_time, route, route2, flight_number, baggage, price)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, ticket_type, date_time, route, route2, flight_number, baggage, price))
    conn.commit()
    conn.close()

def get_last_ticket(user_id):
  """Возвращает последний билет пользователя"""
  conn = create_connection()
  cursor = conn.cursor()
  cursor.execute("""
    SELECT ticket_type, date_time, route, route2, flight_number, baggage, price
    FROM tickets WHERE user_id = ? ORDER BY ticket_id DESC LIMIT 1
  """, (user_id,))
  ticket = cursor.fetchone()
  conn.close()
  return ticket

def get_all_tickets(user_id):
  """Возвращает все билеты пользователя"""
  conn = create_connection()
  cursor = conn.cursor()
  cursor.execute("""SELECT ticket_type, date_time, route, route2, flight_number, baggage, price FROM tickets WHERE user_id = ?""",(user_id,))
  tickets = cursor.fetchall()
  conn.close()
  return tickets

create_tables()
