# add_roles.py
import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy.orm import Session
from sqlalchemy import select
from models.database import SessionLocal, create_tables
from models.tables import Role

def add_roles(db: Session):
    roles = [
        {"role_name": "Бухгалтер", "description": "Финансовый учёт и отчётность"},
        {"role_name": "Менеджер склада", "description": "Управление товарами и закупками"},
        {"role_name": "Продавец", "description": "Работа с заказами и клиентами"}
    ]
    
    for role_data in roles:
        existing = db.scalar(select(Role).filter(Role.role_name == role_data["role_name"]))
        if not existing:
            role = Role(**role_data)
            db.add(role)
            print(f"✅ Роль '{role_data['role_name']}' создана")
        else:
            print(f"⚠️ Роль '{role_data['role_name']}' уже существует")
    
    db.commit()

if __name__ == "__main__":
    create_tables()
    db = SessionLocal()
    add_roles(db)
    db.close()
    print("\n✅ Роли добавлены!")
