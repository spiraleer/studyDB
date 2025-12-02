# init_roles.py (обновлённая версия)
import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy.orm import Session
from sqlalchemy import select
from models.database import SessionLocal
from models.tables import Role, Permission, RolePermission
from core.permissions import PERMISSIONS_BY_ROLE

def assign_permissions_to_role(db: Session, role_name: str):
    role = db.scalar(select(Role).filter(Role.role_name == role_name))
    if not role:
        print(f"Роль '{role_name}' не найдена!")
        return

    permissions = PERMISSIONS_BY_ROLE.get(role_name, [])
    added = 0
    for perm_code in permissions:
        permission = db.scalar(select(Permission).filter(Permission.permission_code == perm_code.value))
        if permission and not db.scalar(select(RolePermission).filter_by(role_id=role.role_id, permission_id=permission.permission_id)):
            db.add(RolePermission(role_id=role.role_id, permission_id=permission.permission_id))
            added += 1
    if added:
        db.commit()
        print(f"  → Добавлено {added} разрешений для роли '{role_name}'")

if __name__ == "__main__":
    from init_permissions import create_permissions
    from models.database import create_tables

    create_tables()
    db = SessionLocal()
    create_permissions(db)

    # Создаём/обновляем роли и назначаем права
    from init_admin import create_initial_admin  # админ создаст свою роль
    create_initial_admin(db)

    roles_to_assign = ["Менеджер склада", "Продавец", "Бухгалтер"]
    for role_name in roles_to_assign:
        role = db.scalar(select(Role).filter(Role.role_name == role_name))
        if role:
            assign_permissions_to_role(db, role_name)

    db.close()
    print("\nРоли и разрешения успешно настроены!")