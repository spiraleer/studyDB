# init_admin.py (БЕЗ ШИФРОВАНИЯ - ТОЛЬКО ДЛЯ ТЕСТОВ)
import sys
import os
import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

# Добавляем корневую папку в путь для корректного импорта модулей
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append('.')

# Импорт моделей и функций БД
from models.database import SessionLocal, create_tables
from models.tables import Role, Employee
# get_password_hash больше не импортируем!

# --- Настройки Админа ---
ADMIN_LOGIN = "admin"
ADMIN_PASSWORD = "admin123" # Пароль будет сохранен как есть!
ADMIN_ROLE_NAME = "Администратор"
# ------------------------

def create_initial_admin(db: Session):
    """Создает роль Администратора и первого сотрудника."""
    try:
        # 1. Поиск/Создание роли
        admin_role = db.scalar(select(Role).filter(Role.role_name == ADMIN_ROLE_NAME))
        
        if not admin_role:
            admin_role = Role(role_name=ADMIN_ROLE_NAME, description="Полный доступ")
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
            print(f"-> Роль '{ADMIN_ROLE_NAME}' создана.")

        # 2. Поиск/Создание сотрудника
        admin_user = db.scalar(select(Employee).filter(Employee.login == ADMIN_LOGIN))
        
        if not admin_user:
            # 🚨 ВАЖНО: Пароль сохраняется в чистом виде!
            raw_password = ADMIN_PASSWORD
            
            admin_user = Employee(
                full_name="Супер Администратор",
                position="Системный администратор",
                role_id=admin_role.role_id,
                hire_date=datetime.date.today(),
                login=ADMIN_LOGIN,
                # Сохраняем чистый пароль
                password_hash=raw_password, 
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print(f"✅ Администратор '{ADMIN_LOGIN}' успешно создан.")
            print(f"   Пароль: {ADMIN_PASSWORD} (Внимание: сохранено без шифрования!)")
        else:
            print(f"⚠️ Сотрудник '{ADMIN_LOGIN}' уже существует. Пропускаем создание.")
        
    except IntegrityError:
        db.rollback()
        print("❌ Ошибка целостности (проверьте уникальность логина). Откат.")
    except Exception as e:
        db.rollback()
        print(f"❌ Произошла ошибка: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    print("--- 1. ПРОВЕРКА ТАБЛИЦ ---")
    create_tables_result = create_tables()
    print(create_tables_result["message"])
    
    print("--- 2. СОЗДАНИЕ АДМИНИСТРАТОРА ---")
    db = SessionLocal()
    create_initial_admin(db)
    print("---------------------------------")