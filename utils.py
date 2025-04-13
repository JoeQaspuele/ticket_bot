def format_order_data(order):
    return (
        f"{order['full_name']}\n"
        f"Дата и время отправления: {order['departure_datetime']}\n"
        f"Маршрут: {order['route1']}"
        + (f" → {order['route2']}" if order.get("route2") else "") + "\n"
        f"Номер рейса/поезда: {order['flight_or_train']}\n"
        f"Транспорт: {order['company']}\n"
        f"Багаж: {'Включен' if order.get('baggage') else 'Без багажа'}\n"
        f"Сумма: {order['price']} рублей"
    )

def format_ticket_data(ticket, full_name):
    message = (
        f"{full_name}\n"
        f"Дата и время отправления: {ticket['date_time']}\n"
    )

    if ticket['is_transfer']:
        message += (
            f"Маршрут первого участка: {ticket['route']}\n"
            f"Маршрут второго участка: {ticket['route_2']}\n"
        )
    else:
        message += f"Маршрут: {ticket['route']}\n"

    message += (
        f"Рейс/поезд: {ticket['flight_number']} {ticket['company']}\n"
        f"Багаж: {'Включен' if ticket['luggage'] == 'yes' else 'Без багажа'}\n"
        f"Сумма: {ticket['amount']} рублей"
    )
    return message
