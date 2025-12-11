# Warehouse Management System

A comprehensive warehouse and sales management system built with FastAPI and PostgreSQL.

## Features

- **User Management**: Role-based access control with permissions
- **Inventory Management**: Product catalog, categories, stock tracking
- **Sales Operations**: Order processing, customer management, payments
- **Purchase Management**: Supplier management, purchase orders
- **Audit Trail**: Complete logging of user actions and data changes
- **Price History**: Automatic tracking of price changes
- **Stock Movements**: Real-time inventory tracking
- **Dashboard**: Analytics and reporting interface

## Tech Stack

- **Backend**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with bcrypt password hashing
- **Frontend**: Jinja2 templates with vanilla JavaScript
- **Server**: Uvicorn ASGI server

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables in `.env`:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
SECRET_KEY=your-secret-key
DEBUG=True
ENVIRONMENT=development
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256
```

4. Initialize the database:
```bash
psql -U postgres -d your_database -f databasecode.sql
```

5. Set up roles and permissions:
```bash
python init_roles.py
python init_permissions.py
python init_admin.py
```

## Running

```bash
python app.py
```

Or with uvicorn:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- `/health` - Health check
- `/api/docs` - API documentation (development only)
- `/login` - Authentication
- `/dashboard` - Main dashboard
- `/api/products` - Product management
- `/api/orders` - Order management
- `/api/customers` - Customer management
- `/api/suppliers` - Supplier management
- `/api/employees` - Employee management
- `/api/purchases` - Purchase management
- `/api/audit` - Audit logs

## Database Schema

The system includes 17 tables:
- Role, Employee, Permission, Role_Permission
- Category, Product, Customer, Supplier
- Orders, Orders_Item, Payment
- Purchase, Purchase_Item
- Price_History, Stock_Movement
- Audit_Log, User_Session

## Security

- Password hashing with bcrypt
- JWT-based authentication
- Role-based access control
- Session management
- Audit logging for all critical operations

## License

Proprietary
