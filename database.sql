-- 1. Таблица категорий товаров (соответствует документации)
CREATE TABLE Category (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at DATE DEFAULT CURRENT_DATE
);

-- 2. Таблица сотрудников (соответствует документации)
CREATE TABLE Employee (
    employee_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    position VARCHAR(50) NOT NULL,
    hire_date DATE NOT NULL,
    salary DECIMAL(10,2) CHECK (salary >= 0),
    login VARCHAR(50) UNIQUE,
    password_hash VARCHAR(255)
);

-- 3. Таблица клиентов (добавлены поля из документации)
CREATE TABLE Customer (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL, -- Изменено с first_name/last_name
    phone VARCHAR(20) UNIQUE NOT NULL, -- Изменено с phone_number
    email VARCHAR(100) UNIQUE,
    loyalty_card_number VARCHAR(20) UNIQUE,
    registration_date DATE DEFAULT CURRENT_DATE
);

-- 4. Таблица поставщиков (соответствует)
CREATE TABLE Supplier (
    supplier_id SERIAL PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    inn VARCHAR(20),
    kpp VARCHAR(20),
    address TEXT,
    contact_phone VARCHAR(20),
    contact_email VARCHAR(100)
);

-- 5. Таблица товаров (изменена согласно документации)
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
    weight DECIMAL(10,3), -- Добавлено из документации
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES Category(category_id),
    FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id)
);

-- 6. Таблица заказов (Orders вместо Sale как в документации)
CREATE TABLE Orders (
    order_id SERIAL PRIMARY KEY,
    order_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    customer_id INT,
    total_amount DECIMAL(10,2) NOT NULL CHECK (total_amount >= 0),
    status VARCHAR(20) NOT NULL CHECK (status IN ('Принят', 'В обработке', 'Оплачен', 'Завершен', 'Отменен')),
    employee_id INT NOT NULL,
    discount_percent DECIMAL(5,2) DEFAULT 0 CHECK (discount_percent BETWEEN 0 AND 99),
    final_amount DECIMAL(10,2) GENERATED ALWAYS AS (total_amount * (1 - discount_percent/100)) STORED,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
);

-- 7. Таблица позиций в заказе (Orders_Item вместо Sale_Item)
CREATE TABLE Orders_Item (
    order_item_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    item_price DECIMAL(10,2) NOT NULL CHECK (item_price > 0), -- Изменено с unit_price
    item_discount DECIMAL(5,2) DEFAULT 0 CHECK (item_discount BETWEEN 0 AND 99),
    total_price DECIMAL(10,2) GENERATED ALWAYS AS (quantity * item_price * (1 - item_discount/100)) STORED,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES Product(product_id),
    UNIQUE(order_id, product_id)
);

-- 8. Таблица платежей (добавлена согласно документации)
CREATE TABLE Payment (
    payment_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL,
    payment_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    payment_type VARCHAR(20) NOT NULL CHECK (payment_type IN ('cash', 'card', 'online')),
    payment_status VARCHAR(20) NOT NULL CHECK (payment_status IN ('Оплачено', 'В ожидании', 'Отменено')),
    FOREIGN KEY (order_id) REFERENCES Orders(order_id)
);

-- 9. Таблица закупок (Purchase остается)
CREATE TABLE Purchase (
    purchase_id SERIAL PRIMARY KEY,
    purchase_date DATE NOT NULL,
    supplier_id INT NOT NULL,
    total_amount DECIMAL(10,2) CHECK (total_amount >= 0),
    delivery_date DATE,
    employee_id INT NOT NULL,
    status VARCHAR(20) DEFAULT 'ordered' CHECK (status IN ('ordered', 'delivered', 'cancelled')),
    FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id),
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
);

-- 10. Таблица позиций в закупке (Purchase_Item остается)
CREATE TABLE Purchase_Item (
    purchase_item_id SERIAL PRIMARY KEY,
    purchase_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL CHECK (unit_price > 0),
    total_price DECIMAL(10,2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
    FOREIGN KEY (purchase_id) REFERENCES Purchase(purchase_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES Product(product_id),
    UNIQUE(purchase_id, product_id)
);

-- 11. Таблица истории цен (остается)
CREATE TABLE Price_History (
    price_history_id SERIAL PRIMARY KEY,
    product_id INT NOT NULL,
    old_price DECIMAL(10,2),
    new_price DECIMAL(10,2) NOT NULL,
    change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by_employee_id INT,
    FOREIGN KEY (product_id) REFERENCES Product(product_id),
    FOREIGN KEY (changed_by_employee_id) REFERENCES Employee(employee_id)
);

-- 12. Таблица движений товаров (остается)
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
    FOREIGN KEY (product_id) REFERENCES Product(product_id),
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
);

-- Создание индексов для оптимизации запросов
CREATE INDEX idx_product_category ON Product(category_id);
CREATE INDEX idx_product_supplier ON Product(supplier_id);
CREATE INDEX idx_orders_customer ON Orders(customer_id);
CREATE INDEX idx_orders_employee ON Orders(employee_id);
CREATE INDEX idx_orders_date ON Orders(order_date);
CREATE INDEX idx_orders_status ON Orders(status);
CREATE INDEX idx_payment_order ON Payment(order_id);
CREATE INDEX idx_payment_status ON Payment(payment_status);
CREATE INDEX idx_purchase_supplier ON Purchase(supplier_id);
CREATE INDEX idx_purchase_employee ON Purchase(employee_id);
CREATE INDEX idx_stock_movement_product ON Stock_Movement(product_id);
CREATE INDEX idx_stock_movement_date ON Stock_Movement(movement_date);

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
        INSERT INTO Price_History (product_id, old_price, new_price, changed_by_employee_id)
        VALUES (NEW.product_id, OLD.price, NEW.price, 1); -- 1 можно заменить на текущего сотрудника
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_log_price_change
    AFTER UPDATE OF price ON Product
    FOR EACH ROW
    EXECUTE FUNCTION log_price_change();

-- Триггер для автоматического создания платежа при оформлении заказа
CREATE OR REPLACE FUNCTION create_payment_on_order()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'Оплачен' THEN
        INSERT INTO Payment (order_id, amount, payment_type, payment_status)
        VALUES (NEW.order_id, NEW.final_amount, 'cash', 'Оплачено');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_create_payment
    AFTER UPDATE OF status ON Orders
    FOR EACH ROW
    WHEN (NEW.status = 'Оплачен')
    EXECUTE FUNCTION create_payment_on_order();