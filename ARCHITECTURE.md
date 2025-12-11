# Архитектура веб-приложения

## Обзор

Система управления складом построена на основе трехслойной архитектуры с использованием FastAPI и PostgreSQL.

## Архитектурные слои

### 1. Слой представления (Presentation Layer)
- **Технологии**: Jinja2 Templates, HTML, CSS, JavaScript
- **Компоненты**:
  - `templates/` - HTML шаблоны страниц
  - `static/` - статические файлы (CSS, JS)
  - Клиентская логика для взаимодействия с API

### 2. Слой бизнес-логики (Business Logic Layer)
- **Технологии**: FastAPI, Python
- **Компоненты**:
  - `routes/` - API эндпоинты и обработчики запросов
  - `core/` - основная бизнес-логика
  - `dependencies.py` - зависимости и middleware

### 3. Слой данных (Data Layer)
- **Технологии**: SQLAlchemy ORM, PostgreSQL
- **Компоненты**:
  - `models/` - модели данных и работа с БД
  - `schemas/` - Pydantic схемы для валидации

## Структура проекта

```
studyDB/
├── app.py                    # Точка входа приложения
├── dependencies.py           # Общие зависимости FastAPI
├── requirements.txt          # Python зависимости
│
├── core/                     # Ядро системы
│   ├── security.py          # Хеширование паролей
│   ├── sessions.py          # Управление сессиями
│   ├── permissions.py       # Коды разрешений
│   └── mapping.py           # Маппинг данных
│
├── models/                   # Модели данных
│   ├── database.py          # Подключение к БД
│   └── tables.py            # ORM модели таблиц
│
├── schemas/                  # Pydantic схемы
│   ├── product.py           # Схемы для товаров
│   └── category.py          # Схемы для категорий
│
├── routes/                   # API маршруты
│   ├── auth.py              # Аутентификация
│   ├── dashboard.py         # Дашборд
│   ├── products.py          # Управление товарами
│   ├── orders.py            # Управление заказами
│   ├── customers.py         # Управление клиентами
│   ├── suppliers.py         # Управление поставщиками
│   ├── employees.py         # Управление сотрудниками
│   ├── purchases.py         # Управление закупками
│   ├── categories.py        # Управление категориями
│   ├── payments.py          # Управление платежами
│   ├── price_history.py     # История цен
│   ├── stock_movements.py   # Движение товаров
│   └── audit.py             # Журнал аудита
│
├── templates/                # HTML шаблоны
│   ├── index.html
│   ├── login.html
│   ├── dashboard.html
│   └── ...
│
└── static/                   # Статические файлы
    ├── css/
    ├── dark-theme.css
    └── theme-switcher.js
```

## Компоненты системы

### Аутентификация и авторизация

**Механизм**:
- Хеширование паролей: PBKDF2-HMAC-SHA256 с солью
- Сессии: токены сохраняются в cookies
- RBAC: роли и разрешения через таблицы Role, Permission, Role_Permission

**Поток аутентификации**:
1. Пользователь отправляет логин/пароль → `/api/auth/token`
2. Система проверяет credentials через `verify_password()`
3. Генерируется session_token
4. Токен сохраняется в cookies
5. При запросах проверяется через `get_current_user()`
6. Разрешения проверяются через `require_permission()`

### Управление данными

**ORM модели** (`models/tables.py`):
- 17 таблиц с relationships
- Автоматические триггеры для updated_at
- Каскадные удаления через ON DELETE CASCADE

**Основные сущности**:
- **Пользователи**: Role, Employee, Permission
- **Товары**: Product, Category, Supplier
- **Продажи**: Orders, Orders_Item, Payment, Customer
- **Закупки**: Purchase, Purchase_Item
- **Аудит**: Audit_Log, User_Session, Price_History, Stock_Movement

### API эндпоинты

**Паттерн маршрутизации**:
```python
router = APIRouter(prefix="/api/products", tags=["Товары"])

@router.get("/")                    # Список
@router.get("/{id}")                # Детали
@router.post("/")                   # Создание
@router.put("/{id}")                # Обновление
@router.delete("/{id}")             # Удаление
```

**Защита эндпоинтов**:
```python
current_user: Employee = Depends(require_permission(PermissionCode.PRODUCTS_VIEW))
```

### Валидация данных

**Pydantic схемы** (`schemas/`):
- `ProductCreate` - создание товара
- `ProductUpdate` - обновление товара
- `ProductResponse` - ответ API

**Преимущества**:
- Автоматическая валидация входных данных
- Типизация и документация API
- Сериализация/десериализация

### База данных

**Архитектура БД**:
- PostgreSQL 12+
- 17 таблиц с индексами
- Триггеры для автоматизации:
  - Обновление updated_at
  - Логирование изменений цен
  - Автоматическое обновление остатков
  - Создание платежей при оплате заказа

**Представления (Views)**:
- `v_active_employees` - активные сотрудники
- `v_role_permissions` - права ролей
- `v_sales_report` - отчет по продажам
- `v_product_stock` - остатки товаров

## Потоки данных

### Создание заказа
```
1. POST /api/orders
   ↓
2. Валидация через OrderCreate схему
   ↓
3. Проверка прав (ORDERS_CREATE)
   ↓
4. Создание Orders + Orders_Item
   ↓
5. Обновление stock_quantity через триггер
   ↓
6. Запись в Stock_Movement
   ↓
7. Возврат OrderResponse
```

### Изменение цены товара
```
1. PUT /api/products/{id}
   ↓
2. Проверка прав (PRODUCTS_EDIT)
   ↓
3. Обновление Product.price
   ↓
4. Триггер создает запись в Price_History
   ↓
5. Обновление updated_at через триггер
   ↓
6. Возврат ProductResponse
```

## Безопасность

### Уровни защиты

1. **Аутентификация**:
   - Хеширование паролей с солью
   - Проверка активности пользователя (is_active)
   - Управление сессиями

2. **Авторизация**:
   - RBAC через Role_Permission
   - Проверка разрешений на уровне эндпоинтов
   - Гранулярный контроль доступа

3. **Аудит**:
   - Логирование всех действий в Audit_Log
   - Сохранение старых/новых значений (JSONB)
   - Отслеживание IP и User-Agent

4. **Валидация**:
   - Pydantic схемы для входных данных
   - Проверка внешних ключей
   - Ограничения на уровне БД (CHECK constraints)

## Масштабируемость

### Текущая архитектура
- Монолитное приложение
- Синхронная обработка запросов
- Одна база данных

### Возможности расширения
- Добавление Redis для кеширования
- Асинхронные задачи через Celery
- Микросервисная архитектура
- Репликация БД для чтения
- API Gateway для балансировки

## Технологический стек

| Компонент | Технология |
|-----------|-----------|
| Backend Framework | FastAPI 0.100+ |
| ORM | SQLAlchemy 2.0+ |
| Database | PostgreSQL 12+ |
| Validation | Pydantic 2.0+ |
| Templates | Jinja2 |
| Server | Uvicorn (ASGI) |
| Password Hashing | PBKDF2-HMAC-SHA256 |
| Environment | python-dotenv |

## Конфигурация

**Переменные окружения** (`.env`):
```env
DATABASE_URL=postgresql://user:pass@host:5432/db
SECRET_KEY=<random-key>
DEBUG=True
ENVIRONMENT=development
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256
```

## Инициализация системы

```bash
# 1. Создание структуры БД
psql -U postgres -d dbname -f databasecode.sql

# 2. Инициализация ролей
python init_roles.py

# 3. Инициализация разрешений
python init_permissions.py

# 4. Создание администратора
python init_admin.py

# 5. Запуск приложения
python app.py
```

## Мониторинг и отладка

**Эндпоинты для диагностики**:
- `/health` - статус приложения и БД
- `/api/config` - конфигурация (dev only)
- `/api/db-check` - проверка подключения к БД
- `/api/check-tables` - список таблиц в БД
- `/api/docs` - Swagger UI (dev only)

## Лучшие практики

1. **Разделение ответственности**: каждый модуль отвечает за свою область
2. **Dependency Injection**: использование FastAPI Depends
3. **Типизация**: Python type hints везде
4. **Валидация**: Pydantic схемы для всех API
5. **Безопасность**: проверка прав на каждом эндпоинте
6. **Аудит**: логирование критических операций
7. **Транзакции**: использование db.commit()/rollback()
