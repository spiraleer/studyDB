# core/mapping.py

# Соответствие технического имени таблицы (snake_case) русскому названию
TABLE_NAMES_MAPPING = {
    "role": "Роли пользователей",
    "employee": "Сотрудники",
    "permission": "Права доступа",
    "role_permission": "Связь Роль-Право",
    "category": "Категории товаров",
    "supplier": "Поставщики",
    "product": "Товары",
    "customer": "Клиенты",
    "orders": "Заказы",
    "orders_item": "Позиции заказа",
    "inventory_transaction": "Транзакции склада",
    "audit_log": "Журнал аудита",
    "user_session": "Сессии пользователей",
    "payment": "Платежи",
    "purchase": "Закупки",
    "purchase_item": "Позиции закупок",
    "price_history": "История цен",
    "stock_movement": "Движение товаров",
}

# Соответствие технического имени столбца русскому названию
# Включает все основные столбцы, используемые в схеме
COLUMN_NAMES_MAPPING = {
    # Общие
    "id": "ID",
    "name": "Имя",
    "description": "Описание",
    "created_at": "Дата создания",
    "updated_at": "Дата изменения",
    "is_active": "Активен",
    "log_id": "ID записи",
    
    # role
    "role_id": "ID Роли",
    "role_name": "Название Роли",
    
    # employee
    "employee_id": "ID Сотрудника",
    "full_name": "ФИО",
    "position": "Должность",
    "role_id": "ID Роли",
    "hire_date": "Дата приема",
    "salary": "Зарплата",
    "login": "Логин",
    "password_hash": "Хеш пароля",
    "last_login": "Последний вход",
    
    # product/category/supplier
    "product_id": "ID Товара",
    "product_name": "Название Товара",
    "price": "Цена",
    "stock_quantity": "Остаток",
    "unit": "Ед. изм.",
    "category_id": "ID Категории",
    "category_name": "Название Категории",
    "supplier_id": "ID Поставщика",
    "company_name": "Название компании",
    "contact_person": "Контактное лицо",
    
    # orders/customer
    "order_id": "ID Заказа",
    "order_date": "Дата заказа",
    "customer_id": "ID Клиента",
    "customer_name": "Имя Клиента",
    "total_amount": "Общая сумма",
    "final_amount": "Итоговая сумма",
    "status": "Статус",
    "payment_type": "Тип оплаты",
    "quantity": "Кол-во",
    "discount_percent": "Скидка (%)",
    
    # inventory
    "transaction_id": "ID Транзакции",
    "transaction_type": "Тип транзакции",
    
    # audit
    "action_type": "Тип действия",
    "table_name": "Таблица",
    "record_id": "ID записи",
    "old_values": "Старые значения",
    "new_values": "Новые значения",
    "ip_address": "IP-адрес",
    "user_agent": "User Agent",
    
    # user_session
    "session_id": "ID Сессии",
    "session_token": "Токен сессии",
    "login_time": "Время входа",
    "logout_time": "Время выхода",
    
    # Дополнительные поля
    "barcode": "Штрихкод",
    "weight": "Вес",
    "phone": "Телефон",
    "email": "Эл. почта",
    "address": "Адрес",
    "inn": "ИНН",
    "kpp": "КПП",
    "contact_phone": "Контактный телефон",
    "contact_email": "Контактная почта",
    "created_by_employee_id": "Создал (сотрудник)",
    "updated_by_employee_id": "Обновил (сотрудник)",
    "loyalty_card_number": "Номер карты лояльности",
    "registration_date": "Дата регистрации",
    "notes": "Примечания",
    "movement_id": "ID Движения",
    "movement_type": "Тип движения",
    "movement_date": "Дата движения",
    "reference_id": "ID Ссылки",
    "reference_type": "Тип ссылки",
}

# Маппинг таблиц на иконки Font Awesome
TABLE_ICONS_MAPPING = {
    'role': 'fa-shield-alt',  # Роли - щит
    'employee': 'fa-users',  # Сотрудники
    'permission': 'fa-key',  # Разрешения - ключ
    'role_permission': 'fa-lock',  # Роль-Разрешение - замок
    'category': 'fa-folder',  # Категории - папка
    'product': 'fa-box',  # Товары - коробка
    'customer': 'fa-user-tie',  # Клиенты - пользователь в галстуке
    'supplier': 'fa-truck',  # Поставщики - грузовик
    'orders': 'fa-shopping-cart',  # Заказы - корзина
    'orders_item': 'fa-receipt',  # Позиции заказа - чек
    'payment': 'fa-money-bill',  # Платежи - банкнота
    'purchase': 'fa-shopping-bag',  # Покупки - сумка
    'purchase_item': 'fa-list',  # Позиции покупки - список
    'price_history': 'fa-history',  # История цен - история
    'stock_movement': 'fa-arrows-alt-h',  # Движение товара - стрелки
    'audit_log': 'fa-clipboard-list',  # Аудит - чек-лист
    'user_session': 'fa-sign-in-alt',  # Сессии - вход
    'inventory_transaction': 'fa-arrows-alt-v',  # Транзакции склада
}


def get_russian_name(technical_name: str, map_type: str) -> str:
    """
    Возвращает русское название по техническому имени.
    """
    mapping = COLUMN_NAMES_MAPPING
    if map_type == 'table':
        mapping = TABLE_NAMES_MAPPING
    
    # Если название есть в словаре, возвращаем его, иначе форматируем техническое название
    return mapping.get(technical_name, technical_name.replace("_", " ").capitalize())


def get_table_icon(table_name: str) -> str:
    """
    Возвращает иконку Font Awesome для таблицы.
    """
    return TABLE_ICONS_MAPPING.get(table_name, 'fa-database')