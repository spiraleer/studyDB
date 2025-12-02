# init_permissions.py
import os
import sys
sys.path.append(os.path.dirname(__file__))

from sqlalchemy.orm import Session
from models.database import SessionLocal, create_tables
from models.tables import Permission
from core.permissions import PermissionCode

def create_permissions(db: Session):
    print("Создание системных разрешений...")
    for perm_code in PermissionCode:
        code = perm_code.value
        exists = db.query(Permission).filter(Permission.permission_code == code).first()
        if not exists:
            module = code.split(".")[0]
            description = code.replace(".", " → ").replace("_", " ").capitalize()
            permission = Permission(
                permission_code=code,
                description=description,
                module=module
            )
            db.add(permission)
            print(f"  ✓ {code}")
        else:
            print(f"  – {code} (уже существует)")
    db.commit()
    print("Все разрешения созданы!\n")

if __name__ == "__main__":
    create_tables()
    db = SessionLocal()
    create_permissions(db)
    db.close()