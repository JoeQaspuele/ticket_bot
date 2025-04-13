import telebot
from telebot import types
from datetime import datetime
from settings import BOT_TOKEN, CITY_LIMITS, ADMIN_IDS
from messages import Messages
import database

bot = telebot.TeleBot(BOT_TOKEN)

user_data = {}

def is_registered(user_id):
    """Проверяет, зарегистрирован ли пользователь."""
    return database.get_user(user_id) is not None

def get_limit(city):
    """Получает лимит для города."""
    return CITY_LIMITS.get(city, 0)

def validate_date(date_str):
    """Проверяет формат и корректность даты."""
    try:
        date = datetime.strptime(date_str, "%d.%m.%Y %H:%M")
        return date >= datetime.now()
    except ValueError:
        return False

def validate_number(number_str):
    """Проверяет, является ли строка числом."""
    try:
        float(number_str)
        return True
    except ValueError:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    """Обработчик команды /start."""
    user_id = message.from_user.id
    if is_registered(user_id):
        show_main_menu(message)
    else:
        show_registration_button(message)

def show_registration_button(message):
    """Показывает кнопку регистрации."""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    register_button = types.KeyboardButton("Регистрация")
    markup.add(register_button)
    bot.send_message(message.chat.id, Messages.WELCOME, reply_markup=markup)

def show_main_menu(message):
    """Показывает главное меню."""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    ticket_button = types.KeyboardButton("Заказать билет")
    hotel_button = types.KeyboardButton("Заказать гостиницу")
    view_last_ticket = types.KeyboardButton("Просмотреть последний билет")
    markup.add(ticket_button, hotel_button, view_last_ticket)
    if message.from_user.id in ADMIN_IDS:
      all_tickets = types.KeyboardButton("Просмотреть все билеты")
      markup.add(all_tickets)
    bot.send_message(message.chat.id, Messages.WELCOME_REGISTERED, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Регистрация")
def register(message):
    """Начинает процесс регистрации."""
    user_data[message.from_user.id] = {}
    bot.send_message(message.chat.id, Messages.REGISTER_START)
    bot.register_next_step_handler(message, process_name)

def process_name(message):
    """Обрабатывает имя."""
    if not message.text:
        bot.send_message(message.chat.id, Messages.EMPTY_FIELD)
        bot.register_next_step_handler(message, process_name)
        return
    user_data[message.from_user.id]['name'] = message.text
    bot.send_message(message.chat.id, Messages.REGISTER_LAST_NAME)
    bot.register_next_step_handler(message, process_last_name)

def process_last_name(message):
    """Обрабатывает фамилию."""
    if not message.text:
        bot.send_message(message.chat.id, Messages.EMPTY_FIELD)
        bot.register_next_step_handler(message, process_last_name)
        return
    user_data[message.from_user.id]['last_name'] = message.text
    bot.send_message(message.chat.id, Messages.REGISTER_MIDDLE_NAME)
    bot.register_next_step_handler(message, process_middle_name)

def process_middle_name(message):
    """Обрабатывает отчество."""
    if not message.text:
        bot.send_message(message.chat.id, Messages.EMPTY_FIELD)
        bot.register_next_step_handler(message, process_middle_name)
        return
    user_data[message.from_user.id]['middle_name'] = message.text
    bot.send_message(message.chat.id, Messages.REGISTER_CITY)
    bot.register_next_step_handler(message, process_city)

def process_city(message):
    """Обрабатывает город."""
    if not message.text:
        bot.send_message(message.chat.id, Messages.EMPTY_FIELD)
        bot.register_next_step_handler(message, process_city)
        return
    user_data[message.from_user.id]['city'] = message.text
    fio = f"{user_data[message.from_user.id]['last_name']} {user_data[message.from_user.id]['name']} {user_data[message.from_user.id]['middle_name']}"
    limit = get_limit(user_data[message.from_user.id]['city'])
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    confirm_button = types.KeyboardButton("Подтвердить")
    markup.add(confirm_button)
    bot.send_message(message.chat.id, Messages.REGISTER_CONFIRM(fio, user_data[message.from_user.id]['city'], limit), reply_markup=markup)
    bot.register_next_step_handler(message, confirm_registration)

def confirm_registration(message):
    """Подтверждает регистрацию."""
    if message.text == "Подтвердить":
        user_id = message.from_user.id
        fio = f"{user_data[user_id]['last_name']} {user_data[user_id]['name']} {user_data[user_id]['middle_name']}"
        city = user_data[user_id]['city']
        limit = get_limit(city)
        database.add_user(user_id, fio, city, limit)
        bot.send_message(message.chat.id, Messages.DATA_SAVED)
        show_main_menu(message)
    else:
        bot.send_message(message.chat.id, Messages.ACTION_CANCELLED)
        start(message)

# Обработка заказа билета
@bot.message_handler(func=lambda message: message.text == "Заказать билет")
def order_ticket(message):
    """Начинает процесс заказа билета."""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    plane_button = types.KeyboardButton("✈️ Авиабилет")
    plane_transfer_button = types.KeyboardButton("✈️ Авиабилет (с пересадкой)")
    train_button = types.KeyboardButton(" Ж/д билет")
    train_transfer_button = types.KeyboardButton(" Ж/д билет (с пересадкой)")
    markup.add(plane_button, plane_transfer_button, train_button, train_transfer_button)
    bot.send_message(message.chat.id, Messages.TICKET_TYPE, reply_markup=markup)

# Обработка заказа гостиницы
@bot.message_handler(func=lambda message: message.text == "Заказать гостиницу")
def order_hotel(message):
    """Обрабатывает заказ гостиницы (реализуйте позже)."""
    bot.send_message(message.chat.id, "Функция заказа гостиницы в разработке.")

@bot.message_handler(func=lambda message: message.text == "Просмотреть последний билет")
def view_last_ticket(message):
  user_id = message.from_user.id
  last_ticket = database.get_last_ticket(user_id)
  if last_ticket:
    formatted_ticket = format_ticket_message(last_ticket)
    bot.send_message(message.chat.id, formatted_ticket)
  else:
    bot.send_message(message.chat.id, "У вас нет заказанных билетов.")

@bot.message_handler(func=lambda message: message.text == "Просмотреть все билеты")
def view_all_tickets(message):
  user_id = message.from_user.id
  if user_id in ADMIN_IDS:
    all_tickets = database.get_all_tickets(user_id)
    if all_tickets:
      formatted_tickets = "\n\n".join([format_ticket_message(ticket) for ticket in all_tickets])
      bot.send_message(message.chat.id, formatted_tickets)
    else:
      bot.send_message(message.chat.id, "Нет заказанных билетов.")
  else:
    bot.send_message(message.chat.id, "Нет доступа.")

def format_ticket_message(ticket):
  ticket_type, date_time, route, route2, flight_number, baggage, price = ticket
  message = f"Тип билета: {ticket_type}\n" \
            f"Дата и время: {date_time}\n" \
            f"Маршрут: {route}\n"
  if route2:
    message += f"Маршрут 2: {route2}\n"
  message += f"Номер рейса/поезда: {flight_number}\n" \
             f"Багаж: {baggage}\n" \
             f"Цена: {price}"
  return message

# Обработка выбора типа билета
@bot.message_handler(func=lambda message: message.text in ["✈️ Авиабилет", "✈️ Авиабилет (с пересадкой)", " Ж/д билет", " Ж/д билет (с пересадкой)"])
def process_ticket_type(message):
    """Обрабатывает выбор типа билета."""
    user_data[message.from_user.id] = {'ticket_type': message.text}
    bot.send_message(message.chat.id, Messages.TICKET_DATE)
    bot.register_next_step_handler(message, process_date)

def process_date(message):
    """Обрабатывает дату и время отправления."""
    if not validate_date(message.text):
        bot.send_message(message.chat.id, Messages.INVALID_DATE)
        bot.register_next_step_handler(message, process_date)
        return
    user_data[message.from_user.id]['date_time'] = message.text
    if "пересадкой" in user_data[message.from_user.id]['ticket_type']:
        bot.send_message(message.chat.id, "Напишите маршрут первого рейса (город отправки и город пересадки), Пример: Уфа - Москва.")
        bot.register_next_step_handler(message, process_route_transfer_1)
    else:
        bot.send_message(message.chat.id, "Напишите маршрут перелета (или проезда), Пример: Уфа - Красноярск.")
        bot.register_next_step_handler(message, process_route)

def process_route_transfer_1(message):
    """Обрабатывает маршрут первого рейса."""
    if not message.text:
        bot.send_message(message.chat.id, Messages.EMPTY_FIELD)
        bot.register_next_step_handler(message, process_route_transfer_1)
        return
    user_data[message.from_user.id]['route'] = message.text
    bot.send_message(message.chat.id, "Напишите маршрут второго рейса (город пересадки - конечная точка), Пример: Москва - Красноярск.")
    bot.register_next_step_handler(message, process_route_transfer_2)

# ... (предыдущий код)

def process_route_transfer_2(message):
    """Обрабатывает маршрут второго рейса."""
    if not message.text:
        bot.send_message(message.chat.id, Messages.EMPTY_FIELD)
        bot.register_next_step_handler(message, process_route_transfer_2)
        return
    user_data[message.from_user.id]['route2'] = message.text
    bot.send_message(message.chat.id, "Напишите название рейса (или номер поезда) и название авиакомпании.")
    bot.register_next_step_handler(message, process_flight_number)

def process_route(message):
    """Обрабатывает маршрут без пересадок."""
    if not message.text:
        bot.send_message(message.chat.id, Messages.EMPTY_FIELD)
        bot.register_next_step_handler(message, process_route)
        return
    user_data[message.from_user.id]['route'] = message.text
    bot.send_message(message.chat.id, "Напишите название рейса (или номер поезда) и название авиакомпании.")
    bot.register_next_step_handler(message, process_flight_number)

def process_flight_number(message):
    """Обрабатывает номер рейса/поезда и авиакомпанию."""
    if not message.text:
        bot.send_message(message.chat.id, Messages.EMPTY_FIELD)
        bot.register_next_step_handler(message, process_flight_number)
        return
    user_data[message.from_user.id]['flight_number'] = message.text
    if "авиабилет" in user_data[message.from_user.id]['ticket_type']:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        baggage_yes = types.KeyboardButton("С багажом")
        baggage_no = types.KeyboardButton("Без багажа")
        markup.add(baggage_yes, baggage_no)
        bot.send_message(message.chat.id, "Выберите, с багажом или без?", reply_markup=markup)
        bot.register_next_step_handler(message, process_baggage)
    else:
        bot.send_message(message.chat.id, "Напишите общую стоимость билетов (только числами).")
        bot.register_next_step_handler(message, process_price)

def process_baggage(message):
    """Обрабатывает информацию о багаже."""
    if message.text not in ["С багажом", "Без багажа"]:
        bot.send_message(message.chat.id, "Пожалуйста, выберите из предложенных вариантов.")
        bot.register_next_step_handler(message, process_baggage)
        return
    user_data[message.from_user.id]['baggage'] = message.text
    bot.send_message(message.chat.id, "Напишите общую стоимость билетов (только числами).")
    bot.register_next_step_handler(message, process_price)

def process_price(message):
    """Обрабатывает стоимость билетов."""
    if not validate_number(message.text):
        bot.send_message(message.chat.id, Messages.INVALID_NUMBER)
        bot.register_next_step_handler(message, process_price)
        return
    user_data[message.from_user.id]['price'] = float(message.text)
    user_id = message.from_user.id
    user_info = database.get_user(user_id)
    limit = user_info[2]
    if user_data[user_id]['price'] > limit:
        bot.send_message(message.chat.id, "Превышен лимит. Необходимо заполнить заявление на удержание денежных средств.")
    show_ticket_confirmation(message)

def show_ticket_confirmation(message):
    """Показывает подтверждение заказа билета."""
    user_id = message.from_user.id
    ticket_info = user_data[user_id]
    fio = database.get_user(user_id)[0]
    confirmation_message = f"{fio}\n" \
                           f"Дата и время вылета: {ticket_info['date_time']}\n" \
                           f"Маршрут: {ticket_info['route']}\n"
    if 'route2' in ticket_info:
        confirmation_message += f"Маршрут 2: {ticket_info['route2']}\n"
    confirmation_message += f"Номер рейса/поезда: {ticket_info['flight_number']}\n"
    if 'baggage' in ticket_info:
        confirmation_message += f"Багаж: {ticket_info['baggage']}\n"
    confirmation_message += f"Сумма билетов: {ticket_info['price']} рублей.\n\n" \
                           f"Все верно?"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    confirm_button = types.KeyboardButton("Подтвердить")
    markup.add(confirm_button)
    bot.send_message(message.chat.id, confirmation_message, reply_markup=markup)
    bot.register_next_step_handler(message, save_ticket)

def save_ticket(message):
    """Сохраняет информацию о билете в базу данных."""
    if message.text == "Подтвердить":
        user_id = message.from_user.id
        ticket_info = user_data[user_id]
        database.add_ticket(user_id, ticket_info['ticket_type'], ticket_info['date_time'],
                            ticket_info.get('route'), ticket_info.get('route2'),
                            ticket_info['flight_number'], ticket_info.get('baggage'),
                            ticket_info['price'])
        bot.send_message(message.chat.id, Messages.DATA_SAVED)
        show_main_menu(message)
    else:
        bot.send_message(message.chat.id, Messages.ACTION_CANCELLED)
        show_main_menu(message)

# ... (остальной код)
