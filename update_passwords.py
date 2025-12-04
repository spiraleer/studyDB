# update_passwords.py - Скрипт для обновления паролей в хешированный вид
from sqlalchemy.orm import Session
from models.database import get_db, engine
from models.tables import Employee
from core.security import hash_password
from sqlalchemy import select

def update_passwords():
    """Обновляет все пароли в БД на хешированные"""
    with Session(engine) as db:
        # Получаем всех сотрудников
        employees = db.scalars(select(Employee)).all()
        
        for employee in employees:
            # Если пароль не хеширован (не содержит :)
            if ':' not in employee.password_hash:
                print(f"Обновляем пароль для {employee.login}")
                # Хешируем текущий пароль
                employee.password_hash = hash_password(employee.password_hash)
        
        db.commit()
        print("Все пароли обновлены!")

if __name__ == "__main__":
    update_passwords()