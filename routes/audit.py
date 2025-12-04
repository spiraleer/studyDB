from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models.database import get_db
from models.tables import AuditLog, Employee
from core.mapping import TABLE_NAMES_MAPPING

router = APIRouter(prefix="/api/audit", tags=["audit"])

@router.get("/")
def get_audit_logs(limit: int = 100, db: Session = Depends(get_db)):
    logs = db.query(AuditLog).order_by(desc(AuditLog.created_at)).limit(limit).all()
    result = []
    for log in logs:
        employee = db.query(Employee).filter(Employee.employee_id == log.employee_id).first()
        table_display = TABLE_NAMES_MAPPING.get(log.table_name, log.table_name) if log.table_name else "Неизвестно"
        result.append({
            "log_id": log.log_id,
            "employee_id": log.employee_id,
            "employee_name": employee.full_name if employee else "Неизвестно",
            "action_type": log.action_type,
            "table_name": log.table_name,
            "table_display": table_display,
            "record_id": log.record_id,
            "old_values": log.old_values,
            "new_values": log.new_values,
            "ip_address": str(log.ip_address) if log.ip_address else None,
            "created_at": log.created_at.isoformat() if log.created_at else None
        })
    return result
