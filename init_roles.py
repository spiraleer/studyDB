# init_roles.py
import sys
import os
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

# Добавляем корневую папку в путь для корректного импорта модулей
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append('.')

# Импорт моделей и функций БД
from models.database import SessionLocal, create_tables
from models.tables import Role

# --- Список дополнительных ролей ---
ROLES_TO_ADD = [
    {
        "role_name": "Менеджер склада",
        "description": "Управление запасами, приемом, перемещением и инвентаризацией товаров."
    },
    {
        "role_name": "Продавец",
        "description": "Создание заказов, обработка продаж и работа с клиентами."
    },
    {
        "role_name": "Бухгалтер",
        "description": "Формирование финансовых отчетов, управление ценами и поставщиками."
    }
]
# -----------------------------------

def create_initial_roles(db: Session):
    """
    Добавляет стандартные роли в базу данных, если они не существуют.
    """
    print("--- ДОБАВЛЕНИЕ СТАНДАРТНЫХ РОЛЕЙ ---")
    
    for role_data in ROLES_TO_ADD:
        role_name = role_data["role_name"]
        
        # Проверяем, существует ли роль
        existing_role = db.scalar(select(Role).filter(Role.role_name == role_name))
        
        if not existing_role:
            try:
                new_role = Role(
                    role_name=role_name,
                    description=role_data["description"]
                )
                db.add(new_role)
                db.commit()
                print(f"✅ Роль '{role_name}' успешно добавлена.")
            except IntegrityError:
                db.rollback()
                print(f"❌ Ошибка: Роль '{role_name}' уже существует.")
            except Exception as e:
                db.rollback()
                print(f"❌ Произошла ошибка при добавлении роли '{role_name}': {e}")
        else:
            print(f"⚠️ Роль '{role_name}' уже существует. Пропускаем.")
    
    print("---------------------------------------")
    db.close()


if __name__ == "__main__":
    # Убедимся, что таблицы созданы
    create_tables_result = create_tables()
    print(f"Статус таблиц: {create_tables_result['message']}")
    
    db = SessionLocal()
    create_initial_roles(db)