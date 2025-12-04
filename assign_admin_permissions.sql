-- Назначение всех прав роли "Администратор"
INSERT INTO role_permission (role_id, permission_id)
SELECT r.role_id, p.permission_id
FROM role r, permission p
WHERE r.role_name = 'Администратор'
AND NOT EXISTS (
    SELECT 1 FROM role_permission rp 
    WHERE rp.role_id = r.role_id AND rp.permission_id = p.permission_id
);

-- Проверка
SELECT COUNT(*) as admin_permissions_count
FROM role_permission rp
JOIN role r ON r.role_id = rp.role_id
WHERE r.role_name = 'Администратор';
