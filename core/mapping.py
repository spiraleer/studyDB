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