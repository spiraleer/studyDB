# core/permissions.py
from enum import StrEnum

class PermissionCode(StrEnum):
    # Система
    VIEW_DASHBOARD = "system.view_dashboard"
    VIEW_AUDIT_LOG = "system.view_audit_log"
    VIEW_USER_SESSIONS = "system.view_sessions"

    # Сотрудники и роли
    EMPLOYEES_VIEW = "employees.view"
    EMPLOYEES_CREATE = "employees.create"
    EMPLOYEES_EDIT = "employees.edit"
    EMPLOYEES_DELETE = "employees.delete"
    ROLES_MANAGE = "roles.manage"

    # Товары и склад
    PRODUCTS_VIEW = "products.view"
    PRODUCTS_CREATE = "products.create"
    PRODUCTS_EDIT = "products.edit"
    PRODUCTS_DELETE = "products.delete"
    STOCK_MOVEMENT = "stock.movement"
    PRICE_CHANGE = "price.change"

    # Заказы и продажи
    ORDERS_VIEW = "orders.view"
    ORDERS_CREATE = "orders.create"
    ORDERS_EDIT = "orders.edit"
    ORDERS_CANCEL = "orders.cancel"

    # Закупки
    PURCHASES_VIEW = "purchases.view"
    PURCHASES_CREATE = "purchases.create"

    # Клиенты и поставщики
    CUSTOMERS_VIEW = "customers.view"
    CUSTOMERS_MANAGE = "customers.manage"
    SUPPLIERS_VIEW = "suppliers.view"
    SUPPLIERS_MANAGE = "suppliers.manage"

    # Отчёты
    REPORTS_VIEW = "reports.view"
    REPORTS_EXPORT = "reports.export"


# Группировка для удобства
PERMISSIONS_BY_ROLE = {
    "Администратор": [perm for perm in PermissionCode],
    "Менеджер склада": [
        PermissionCode.PRODUCTS_VIEW,
        PermissionCode.PRODUCTS_CREATE,
        PermissionCode.PRODUCTS_EDIT,
        PermissionCode.STOCK_MOVEMENT,
        PermissionCode.PURCHASES_VIEW,
        PermissionCode.PURCHASES_CREATE,
        PermissionCode.SUPPLIERS_VIEW,
        PermissionCode.VIEW_DASHBOARD,
    ],
    "Продавец": [
        PermissionCode.ORDERS_VIEW,
        PermissionCode.ORDERS_CREATE,
        PermissionCode.ORDERS_EDIT,
        PermissionCode.CUSTOMERS_VIEW,
        PermissionCode.CUSTOMERS_MANAGE,
        PermissionCode.PRODUCTS_VIEW,
        PermissionCode.VIEW_DASHBOARD,
    ],
    "Бухгалтер": [
        PermissionCode.REPORTS_VIEW,
        PermissionCode.REPORTS_EXPORT,
        PermissionCode.ORDERS_VIEW,
        PermissionCode.PURCHASES_VIEW,
        PermissionCode.PRICE_CHANGE,
        PermissionCode.PRODUCTS_VIEW,
        PermissionCode.VIEW_DASHBOARD,
    ],
}