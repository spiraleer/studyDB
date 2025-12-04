-- Добавление новых ролей
INSERT INTO role (role_name, description) 
SELECT 'Бухгалтер', 'Финансовый учёт и отчётность'
WHERE NOT EXISTS (SELECT 1 FROM role WHERE role_name = 'Бухгалтер');

INSERT INTO role (role_name, description) 
SELECT 'Менеджер склада', 'Управление товарами и закупками'
WHERE NOT EXISTS (SELECT 1 FROM role WHERE role_name = 'Менеджер склада');

INSERT INTO role (role_name, description) 
SELECT 'Продавец', 'Работа с заказами и клиентами'
WHERE NOT EXISTS (SELECT 1 FROM role WHERE role_name = 'Продавец');

-- Проверка созданных ролей
SELECT * FROM role;
