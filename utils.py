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

