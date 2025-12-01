-- 1. Таблица ролей пользователей
CREATE TABLE Role (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Таблица сотрудников с привязкой к роли
CREATE TABLE Employee (
    employee_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    position VARCHAR(50) NOT NULL,
    role_id INT NOT NULL,
    hire_date DATE NOT NULL,
    salary DECIMAL(10,2) CHECK (salary >= 0),
    login VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES Role(role_id)
);

-- 3. Таблица прав доступа (разрешения)
CREATE TABLE Permission (
    permission_id SERIAL PRIMARY KEY,
    permission_code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    module VARCHAR(50) NOT NULL
);

-- 4. Таблица связи ролей и прав (многие-ко-многим)
CREATE TABLE Role_Permission (
    role_permission_id SERIAL PRIMARY KEY,
    role_id INT NOT NULL,
    permission_id INT NOT NULL,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    granted_by_employee_id INT,
    FOREIGN KEY (role_id) REFERENCES Role(role_id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES Permission(permission_id) ON DELETE CASCADE,
    FOREIGN KEY (granted_by_employee_id) REFERENCES Employee(employee_id),
    UNIQUE(role_id, permission_id)
);

-- 5. Таблица категорий товаров
CREATE TABLE Category (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_employee_id INT,
    updated_at TIMESTAMP,
    updated_by_employee_id INT,
    FOREIGN KEY (created_by_employee_id) REFERENCES Employee(employee_id),
    FOREIGN KEY (updated_by_employee_id) REFERENCES Employee(employee_id)
);

-- 6. Таблица клиентов
CREATE TABLE Customer (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,
    loyalty_card_number VARCHAR(20) UNIQUE,
    registration_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_employee_id INT,
    notes TEXT,
    FOREIGN KEY (created_by_employee_id) REFERENCES Employee(employee_id)
);

-- 7. Таблица поставщиков
CREATE TABLE Supplier (
    supplier_id SERIAL PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    inn VARCHAR(20),
    kpp VARCHAR(20),
    address TEXT,
    contact_phone VARCHAR(20),
    contact_email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_employee_id INT,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (created_by_employee_id) REFERENCES Employee(employee_id)
);

-- 8. Таблица товаров
CREATE TABLE Product (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    description TEXT,
    unit VARCHAR(20) NOT NULL,
    category_id INT NOT NULL,
    price DECIMAL(10,2) NOT NULL CHECK (price > 0),
    stock_quantity INT NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    barcode VARCHAR(50) UNIQUE,
    supplier_id INT,
    weight DECIMAL(10,3),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_employee_id INT,
    updated_at TIMESTAMP,
    updated_by_employee_id INT,
    FOREIGN KEY (category_id) REFERENCES Category(category_id),
    FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id),
    FOREIGN KEY (created_by_employee_id) REFERENCES Employee(employee_id),
    FOREIGN KEY (updated_by_employee_id) REFERENCES Employee(employee_id)
);

-- 9. Таблица заказов
CREATE TABLE Orders (
    order_id SERIAL PRIMARY KEY,
    order_code VARCHAR(20) UNIQUE,
    order_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    customer_id INT,
    total_amount DECIMAL(10,2) NOT NULL CHECK (total_amount >= 0),
    status VARCHAR(20) NOT NULL CHECK (status IN ('Принят', 'В обработке', 'Оплачен', 'Завершен', 'Отменен')),
    employee_id INT NOT NULL,
    discount_percent DECIMAL(5,2) DEFAULT 0 CHECK (discount_percent BETWEEN 0 AND 99),
    final_amount DECIMAL(10,2) GENERATED ALWAYS AS (total_amount * (1 - discount_percent/100)) STORED,
    payment_type VARCHAR(20) CHECK (payment_type IN ('cash', 'card', 'online')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
);

-- 10. Таблица позиций в заказе
CREATE TABLE Orders_Item (
    order_item_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    item_price DECIMAL(10,2) NOT NULL CHECK (item_price > 0),
    item_discount DECIMAL(5,2) DEFAULT 0 CHECK (item_discount BETWEEN 0 AND 99),
    total_price DECIMAL(10,2) GENERATED ALWAYS AS (quantity * item_price * (1 - item_discount/100)) STORED,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES Product(product_id),
    UNIQUE(order_id, product_id)
);

-- 11. Таблица платежей
CREATE TABLE Payment (
    payment_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL,
    payment_code VARCHAR(20) UNIQUE,
    payment_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    payment_type VARCHAR(20) NOT NULL CHECK (payment_type IN ('cash', 'card', 'online')),
    payment_status VARCHAR(20) NOT NULL CHECK (payment_status IN ('Оплачено', 'В ожидании', 'Отменено')),
    employee_id INT NOT NULL,
    receipt_number VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
);

-- 12. Таблица закупок
CREATE TABLE Purchase (
    purchase_id SERIAL PRIMARY KEY,
    purchase_code VARCHAR(20) UNIQUE,
    purchase_date DATE NOT NULL,
    supplier_id INT NOT NULL,
    total_amount DECIMAL(10,2) CHECK (total_amount >= 0),
    delivery_date DATE,
    employee_id INT NOT NULL,
    status VARCHAR(20) DEFAULT 'ordered' CHECK (status IN ('ordered', 'delivered', 'cancelled')),
    invoice_number VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id),
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
);

-- 13. Таблица позиций в закупке
CREATE TABLE Purchase_Item (
    purchase_item_id SERIAL PRIMARY KEY,
    purchase_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL CHECK (unit_price > 0),
    total_price DECIMAL(10,2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (purchase_id) REFERENCES Purchase(purchase_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES Product(product_id),
    UNIQUE(purchase_id, product_id)
);

-- 14. Таблица истории цен
CREATE TABLE Price_History (
    price_history_id SERIAL PRIMARY KEY,
    product_id INT NOT NULL,
    old_price DECIMAL(10,2),
    new_price DECIMAL(10,2) NOT NULL,
    change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by_employee_id INT NOT NULL,
    reason TEXT,
    FOREIGN KEY (product_id) REFERENCES Product(product_id),
    FOREIGN KEY (changed_by_employee_id) REFERENCES Employee(employee_id)
);

-- 15. Таблица движений товаров
CREATE TABLE Stock_Movement (
    movement_id SERIAL PRIMARY KEY,
    product_id INT NOT NULL,
    movement_type VARCHAR(20) NOT NULL CHECK (movement_type IN ('incoming', 'outgoing', 'adjustment')),
    quantity INT NOT NULL,
    movement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reference_id INT,
    reference_type VARCHAR(20),
    employee_id INT NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES Product(product_id),
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
);

-- 16. Таблица логов действий пользователей (для аудита)
CREATE TABLE Audit_Log (
    log_id SERIAL PRIMARY KEY,
    employee_id INT,
    action_type VARCHAR(50) NOT NULL,
    table_name VARCHAR(50),
    record_id INT,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
);

-- 17. Таблица сессий пользователей
CREATE TABLE User_Session (
    session_id SERIAL PRIMARY KEY,
    employee_id INT NOT NULL,
    session_token VARCHAR(255) NOT NULL UNIQUE,
    login_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    logout_time TIMESTAMP,
    ip_address INET,
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
);

-- Создание индексов для оптимизации запросов
CREATE INDEX idx_employee_role ON Employee(role_id);
CREATE INDEX idx_employee_login ON Employee(login);
CREATE INDEX idx_employee_active ON Employee(is_active);
CREATE INDEX idx_role_permission_role ON Role_Permission(role_id);
CREATE INDEX idx_role_permission_permission ON Role_Permission(permission_id);
CREATE INDEX idx_product_category ON Product(category_id);
CREATE INDEX idx_product_supplier ON Product(supplier_id);
CREATE INDEX idx_product_active ON Product(is_active);
CREATE INDEX idx_orders_customer ON Orders(customer_id);
CREATE INDEX idx_orders_employee ON Orders(employee_id);
CREATE INDEX idx_orders_date ON Orders(order_date);
CREATE INDEX idx_orders_status ON Orders(status);
CREATE INDEX idx_orders_code ON Orders(order_code);
CREATE INDEX idx_payment_order ON Payment(order_id);
CREATE INDEX idx_payment_status ON Payment(payment_status);
CREATE INDEX idx_payment_code ON Payment(payment_code);
CREATE INDEX idx_purchase_supplier ON Purchase(supplier_id);
CREATE INDEX idx_purchase_employee ON Purchase(employee_id);
CREATE INDEX idx_purchase_status ON Purchase(status);
CREATE INDEX idx_purchase_code ON Purchase(purchase_code);
CREATE INDEX idx_stock_movement_product ON Stock_Movement(product_id);
CREATE INDEX idx_stock_movement_date ON Stock_Movement(movement_date);
CREATE INDEX idx_audit_log_employee ON Audit_Log(employee_id);
CREATE INDEX idx_audit_log_created ON Audit_Log(created_at);
CREATE INDEX idx_user_session_employee ON User_Session(employee_id);
CREATE INDEX idx_user_session_token ON User_Session(session_token);
CREATE INDEX idx_user_session_active ON User_Session(is_active);

-- Функция для автоматического обновления поля updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Триггеры для обновления updated_at
CREATE TRIGGER update_employee_updated_at
    BEFORE UPDATE ON Employee
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_product_updated_at
    BEFORE UPDATE ON Product
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_category_updated_at
    BEFORE UPDATE ON Category
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Триггер для автоматического обновления остатков при движении товаров
CREATE OR REPLACE FUNCTION update_stock_quantity()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        IF NEW.movement_type = 'incoming' THEN
            UPDATE Product SET stock_quantity = stock_quantity + NEW.quantity 
            WHERE product_id = NEW.product_id;
        ELSIF NEW.movement_type = 'outgoing' THEN
            UPDATE Product SET stock_quantity = stock_quantity - NEW.quantity 
            WHERE product_id = NEW.product_id;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_stock
    AFTER INSERT ON Stock_Movement
    FOR EACH ROW
    EXECUTE FUNCTION update_stock_quantity();

-- Триггер для записи истории изменений цен
CREATE OR REPLACE FUNCTION log_price_change()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.price <> OLD.price THEN
        INSERT INTO Price_History (product_id, old_price, new_price, changed_by_employee_id, reason)
        VALUES (NEW.product_id, OLD.price, NEW.price, NEW.updated_by_employee_id, 'Изменение цены');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_log_price_change
    AFTER UPDATE OF price ON Product
    FOR EACH ROW
    EXECUTE FUNCTION log_price_change();

-- Триггер для автоматического создания платежа при изменении статуса заказа на "Оплачен"
CREATE OR REPLACE FUNCTION create_payment_on_order_paid()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'Оплачен' AND OLD.status != 'Оплачен' THEN
        INSERT INTO Payment (order_id, amount, payment_type, payment_status, employee_id)
        VALUES (NEW.order_id, NEW.final_amount, COALESCE(NEW.payment_type, 'cash'), 'Оплачено', NEW.employee_id);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_create_payment
    AFTER UPDATE OF status ON Orders
    FOR EACH ROW
    EXECUTE FUNCTION create_payment_on_order_paid();

-- Триггер для логирования изменений в таблицах
CREATE OR REPLACE FUNCTION log_audit_trail()
RETURNS TRIGGER AS $$
DECLARE
    v_old_values JSONB;
    v_new_values JSONB;
BEGIN
    IF TG_OP = 'INSERT' THEN
        v_new_values = to_jsonb(NEW);
        INSERT INTO Audit_Log (employee_id, action_type, table_name, record_id, new_values)
        VALUES (NEW.updated_by_employee_id, 'INSERT', TG_TABLE_NAME, NEW.product_id, v_new_values);
    ELSIF TG_OP = 'UPDATE' THEN
        v_old_values = to_jsonb(OLD);
        v_new_values = to_jsonb(NEW);
        INSERT INTO Audit_Log (employee_id, action_type, table_name, record_id, old_values, new_values)
        VALUES (NEW.updated_by_employee_id, 'UPDATE', TG_TABLE_NAME, NEW.product_id, v_old_values, v_new_values);
    ELSIF TG_OP = 'DELETE' THEN
        v_old_values = to_jsonb(OLD);
        INSERT INTO Audit_Log (employee_id, action_type, table_name, record_id, old_values)
        VALUES (OLD.updated_by_employee_id, 'DELETE', TG_TABLE_NAME, OLD.product_id, v_old_values);
    END IF;
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Применяем триггер аудита к важным таблицам
CREATE TRIGGER audit_product_changes
    AFTER INSERT OR UPDATE OR DELETE ON Product
    FOR EACH ROW
    EXECUTE FUNCTION log_audit_trail();

CREATE TRIGGER audit_price_changes
    AFTER INSERT OR UPDATE OR DELETE ON Price_History
    FOR EACH ROW
    EXECUTE FUNCTION log_audit_trail();

-- Функция для проверки пароля (для примера)
CREATE OR REPLACE FUNCTION check_password_strength(password TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    -- Минимальная длина 8 символов, должна содержать буквы и цифры
    RETURN length(password) >= 8 
           AND password ~ '[A-Za-z]' 
           AND password ~ '[0-9]';
END;
$$ LANGUAGE plpgsql;

-- Создание стандартных ролей (будут заполнены позже данными)
COMMENT ON TABLE Role IS 'Таблица ролей пользователей: кассир, менеджер, администратор и т.д.';
COMMENT ON TABLE Permission IS 'Таблица прав доступа к различным функциям системы';
COMMENT ON TABLE Role_Permission IS 'Связь ролей и прав доступа';
COMMENT ON TABLE Audit_Log IS 'Журнал аудита для отслеживания действий пользователей';
COMMENT ON TABLE User_Session IS 'Сессии пользователей для управления доступом';

-- Создание представлений для удобства

-- Представление для просмотра активных сотрудников с ролями
CREATE OR REPLACE VIEW v_active_employees AS
SELECT 
    e.employee_id,
    e.full_name,
    e.position,
    r.role_name,
    e.login,
    e.hire_date,
    e.is_active
FROM Employee e
JOIN Role r ON e.role_id = r.role_id
WHERE e.is_active = TRUE;

-- Представление для просмотра прав ролей
CREATE OR REPLACE VIEW v_role_permissions AS
SELECT 
    r.role_name,
    p.permission_code,
    p.description as permission_description,
    p.module
FROM Role r
JOIN Role_Permission rp ON r.role_id = rp.role_id
JOIN Permission p ON rp.permission_id = p.permission_id
ORDER BY r.role_name, p.module, p.permission_code;

-- Представление для отчетов по продажам
CREATE OR REPLACE VIEW v_sales_report AS
SELECT 
    o.order_id,
    o.order_date,
    c.customer_name,
    e.full_name as employee_name,
    o.total_amount,
    o.discount_percent,
    o.final_amount,
    o.status,
    o.payment_type,
    COUNT(oi.order_item_id) as items_count,
    SUM(oi.quantity) as total_quantity
FROM Orders o
LEFT JOIN Customer c ON o.customer_id = c.customer_id
LEFT JOIN Employee e ON o.employee_id = e.employee_id
LEFT JOIN Orders_Item oi ON o.order_id = oi.order_id
GROUP BY o.order_id, o.order_date, c.customer_name, e.full_name, o.total_amount, 
         o.discount_percent, o.final_amount, o.status, o.payment_type;

-- Представление для отслеживания остатков товаров
CREATE OR REPLACE VIEW v_product_stock AS
SELECT 
    p.product_id,
    p.product_name,
    c.category_name,
    p.price,
    p.stock_quantity,
    p.unit,
    s.company_name as supplier_name,
    CASE 
        WHEN p.stock_quantity = 0 THEN 'Нет в наличии'
        WHEN p.stock_quantity < 10 THEN 'Мало'
        ELSE 'В наличии'
    END as stock_status,
    p.is_active
FROM Product p
LEFT JOIN Category c ON p.category_id = c.category_id
LEFT JOIN Supplier s ON p.supplier_id = s.supplier_id;

-- Комментарии к таблицам
COMMENT ON TABLE Product IS 'Таблица товаров с информацией о ценах и остатках';
COMMENT ON TABLE Orders IS 'Таблица заказов/продаж';
COMMENT ON TABLE Payment IS 'Таблица платежей по заказам';
COMMENT ON TABLE Purchase IS 'Таблица закупок товаров у поставщиков';
COMMENT ON TABLE Stock_Movement IS 'Таблица движения товаров на складе';
COMMENT ON TABLE Price_History IS 'История изменений цен на товары';