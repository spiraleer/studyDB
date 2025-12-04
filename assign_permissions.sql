-- Назначение прав для роли "Менеджер склада"
INSERT INTO role_permission (role_id, permission_id)
SELECT r.role_id, p.permission_id
FROM role r, permission p
WHERE r.role_name = 'Менеджер склада'
AND p.permission_code IN (
    'products.view',
    'products.create',
    'products.edit',
    'stock.movement',
    'purchases.view',
    'purchases.create',
    'suppliers.view',
    'system.view_dashboard'
)
AND NOT EXISTS (
    SELECT 1 FROM role_permission rp 
    WHERE rp.role_id = r.role_id AND rp.permission_id = p.permission_id
);

-- Назначение прав для роли "Продавец"
INSERT INTO role_permission (role_id, permission_id)
SELECT r.role_id, p.permission_id
FROM role r, permission p
WHERE r.role_name = 'Продавец'
AND p.permission_code IN (
    'orders.view',
    'orders.create',
    'orders.edit',
    'customers.view',
    'customers.manage',
    'products.view',
    'system.view_dashboard'
)
AND NOT EXISTS (
    SELECT 1 FROM role_permission rp 
    WHERE rp.role_id = r.role_id AND rp.permission_id = p.permission_id
);

-- Назначение прав для роли "Бухгалтер"
INSERT INTO role_permission (role_id, permission_id)
SELECT r.role_id, p.permission_id
FROM role r, permission p
WHERE r.role_name = 'Бухгалтер'
AND p.permission_code IN (
    'reports.view',
    'reports.export',
    'orders.view',
    'purchases.view',
    'price.change',
    'products.view',
    'system.view_dashboard'
)
AND NOT EXISTS (
    SELECT 1 FROM role_permission rp 
    WHERE rp.role_id = r.role_id AND rp.permission_id = p.permission_id
);

-- Проверка назначенных прав
SELECT r.role_name, p.permission_code
FROM role r
JOIN role_permission rp ON r.role_id = rp.role_id
JOIN permission p ON rp.permission_id = p.permission_id
WHERE r.role_name IN ('Менеджер склада', 'Продавец', 'Бухгалтер')
ORDER BY r.role_name, p.permission_code;
