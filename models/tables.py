# models/tables.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, ForeignKey, Text, DECIMAL, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Role(Base):
    __tablename__ = "role"
    
    role_id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    employees = relationship("Employee", back_populates="role")
    permissions = relationship("Permission", secondary="role_permission", back_populates="roles")

class Employee(Base):
    __tablename__ = "employee"
    
    employee_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    position = Column(String(50), nullable=False)
    role_id = Column(Integer, ForeignKey("role.role_id"), nullable=False)
    hire_date = Column(Date, nullable=False)
    salary = Column(DECIMAL(10, 2))
    login = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    role = relationship("Role", back_populates="employees")
    created_categories = relationship("Category", foreign_keys="Category.created_by_employee_id")
    created_customers = relationship("Customer", foreign_keys="Customer.created_by_employee_id")
    created_products = relationship("Product", foreign_keys="Product.created_by_employee_id")
    orders = relationship("Orders", back_populates="employee")

class Permission(Base):
    __tablename__ = "permission"
    
    permission_id = Column(Integer, primary_key=True, index=True)
    permission_code = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    module = Column(String(50), nullable=False)
    
    # Связи
    roles = relationship("Role", secondary="role_permission", back_populates="permissions")

class RolePermission(Base):
    __tablename__ = "role_permission"
    
    role_permission_id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("role.role_id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permission.permission_id"), nullable=False)
    granted_at = Column(DateTime(timezone=True), server_default=func.now())
    granted_by_employee_id = Column(Integer, ForeignKey("employee.employee_id"))

class Category(Base):
    __tablename__ = "category"
    
    category_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by_employee_id = Column(Integer, ForeignKey("employee.employee_id"))
    updated_at = Column(DateTime(timezone=True))
    updated_by_employee_id = Column(Integer, ForeignKey("employee.employee_id"))
    
    # Связи
    products = relationship("Product", back_populates="category")
    created_by = relationship("Employee", foreign_keys=[created_by_employee_id])
    updated_by = relationship("Employee", foreign_keys=[updated_by_employee_id])

class Customer(Base):
    __tablename__ = "customer"
    
    customer_id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    email = Column(String(100), unique=True)
    loyalty_card_number = Column(String(20), unique=True)
    registration_date = Column(Date, server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by_employee_id = Column(Integer, ForeignKey("employee.employee_id"))
    notes = Column(Text)
    
    # Связи
    orders = relationship("Orders", back_populates="customer")
    created_by = relationship("Employee", foreign_keys=[created_by_employee_id])

class Supplier(Base):
    __tablename__ = "supplier"
    
    supplier_id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(100), nullable=False)
    inn = Column(String(20))
    kpp = Column(String(20))
    address = Column(Text)
    contact_phone = Column(String(20))
    contact_email = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by_employee_id = Column(Integer, ForeignKey("employee.employee_id"))
    is_active = Column(Boolean, default=True)
    
    # Связи
    products = relationship("Product", back_populates="supplier")
    purchases = relationship("Purchase", back_populates="supplier")

class Product(Base):
    __tablename__ = "product"
    
    product_id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(100), nullable=False)
    description = Column(Text)
    unit = Column(String(20), nullable=False)
    category_id = Column(Integer, ForeignKey("category.category_id"), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    stock_quantity = Column(Integer, default=0)
    barcode = Column(String(50), unique=True)
    supplier_id = Column(Integer, ForeignKey("supplier.supplier_id"))
    weight = Column(DECIMAL(10, 3))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by_employee_id = Column(Integer, ForeignKey("employee.employee_id"))
    updated_at = Column(DateTime(timezone=True))
    updated_by_employee_id = Column(Integer, ForeignKey("employee.employee_id"))
    
    # Связи
    category = relationship("Category", back_populates="products")
    supplier = relationship("Supplier", back_populates="products")
    created_by = relationship("Employee", foreign_keys=[created_by_employee_id])
    updated_by = relationship("Employee", foreign_keys=[updated_by_employee_id])
    order_items = relationship("OrderItem", back_populates="product")

class Orders(Base):
    __tablename__ = "orders"
    
    order_id = Column(Integer, primary_key=True, index=True)
    order_code = Column(String(20), unique=True)
    order_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    customer_id = Column(Integer, ForeignKey("customer.customer_id"))
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    status = Column(String(20), nullable=False)  # Принят, В обработке, Оплачен, Завершен, Отменен
    employee_id = Column(Integer, ForeignKey("employee.employee_id"), nullable=False)
    discount_percent = Column(DECIMAL(5, 2), default=0)
    payment_type = Column(String(20))  # cash, card, online
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True))
    
    # Связи
    customer = relationship("Customer", back_populates="orders")
    employee = relationship("Employee", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    payments = relationship("Payment", back_populates="order")

class OrderItem(Base):
    __tablename__ = "orders_item"
    
    order_item_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=False)
    product_id = Column(Integer, ForeignKey("product.product_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    item_price = Column(DECIMAL(10, 2), nullable=False)
    item_discount = Column(DECIMAL(5, 2), default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    order = relationship("Orders", back_populates="items")
    product = relationship("Product", back_populates="order_items")

class Payment(Base):
    __tablename__ = "payment"
    
    payment_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=False)
    payment_code = Column(String(20), unique=True)
    payment_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    payment_type = Column(String(20), nullable=False)  # cash, card, online
    payment_status = Column(String(20), nullable=False)  # Оплачено, В ожидании, Отменено
    employee_id = Column(Integer, ForeignKey("employee.employee_id"), nullable=False)
    receipt_number = Column(String(50))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    order = relationship("Orders", back_populates="payments")
    employee = relationship("Employee")

class Purchase(Base):
    __tablename__ = "purchase"
    
    purchase_id = Column(Integer, primary_key=True, index=True)
    purchase_code = Column(String(20), unique=True)
    purchase_date = Column(Date, nullable=False)
    supplier_id = Column(Integer, ForeignKey("supplier.supplier_id"), nullable=False)
    total_amount = Column(DECIMAL(10, 2))
    delivery_date = Column(Date)
    employee_id = Column(Integer, ForeignKey("employee.employee_id"), nullable=False)
    status = Column(String(20), default='ordered')  # ordered, delivered, cancelled
    invoice_number = Column(String(50))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    supplier = relationship("Supplier", back_populates="purchases")
    items = relationship("PurchaseItem", back_populates="purchase")

class PurchaseItem(Base):
    __tablename__ = "purchase_item"
    
    purchase_item_id = Column(Integer, primary_key=True, index=True)
    purchase_id = Column(Integer, ForeignKey("purchase.purchase_id"), nullable=False)
    product_id = Column(Integer, ForeignKey("product.product_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    purchase = relationship("Purchase", back_populates="items")
    product = relationship("Product")

class PriceHistory(Base):
    __tablename__ = "price_history"
    
    price_history_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("product.product_id"), nullable=False)
    old_price = Column(DECIMAL(10, 2))
    new_price = Column(DECIMAL(10, 2), nullable=False)
    change_date = Column(DateTime(timezone=True), server_default=func.now())
    changed_by_employee_id = Column(Integer, ForeignKey("employee.employee_id"), nullable=False)
    reason = Column(Text)
    
    # Связи
    product = relationship("Product")
    changed_by = relationship("Employee")

class StockMovement(Base):
    __tablename__ = "stock_movement"
    
    movement_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("product.product_id"), nullable=False)
    movement_type = Column(String(20), nullable=False)  # incoming, outgoing, adjustment
    quantity = Column(Integer, nullable=False)
    movement_date = Column(DateTime(timezone=True), server_default=func.now())
    reference_id = Column(Integer)
    reference_type = Column(String(20))
    employee_id = Column(Integer, ForeignKey("employee.employee_id"), nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    product = relationship("Product")
    employee = relationship("Employee")

class AuditLog(Base):
    __tablename__ = "audit_log"
    
    log_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employee.employee_id"))
    action_type = Column(String(50), nullable=False)
    table_name = Column(String(50))
    record_id = Column(Integer)
    old_values = Column(JSON)
    new_values = Column(JSON)
    ip_address = Column(String(50))
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    employee = relationship("Employee")

class UserSession(Base):
    __tablename__ = "user_session"
    
    session_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employee.employee_id"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False)
    login_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    logout_time = Column(DateTime(timezone=True))
    ip_address = Column(String(50))
    user_agent = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Связи
    employee = relationship("Employee")