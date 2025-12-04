// Универсальный переключатель темы
(function() {
    // Создаем кнопку переключения темы
    const themeToggle = document.createElement('button');
    themeToggle.id = 'theme-toggle';
    themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
    themeToggle.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        border: none;
        background: linear-gradient(45deg, #6a11cb, #2575fc);
        color: white;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(106, 17, 203, 0.3);
        z-index: 1000;
        transition: all 0.3s ease;
        font-size: 18px;
    `;
    
    // Проверяем сохраненную тему
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
        document.documentElement.classList.add('dark-theme');
        themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
    }
    
    // Обработчик переключения
    themeToggle.addEventListener('click', function() {
        const isDark = document.documentElement.classList.contains('dark-theme');
        
        if (isDark) {
            document.documentElement.classList.remove('dark-theme');
            localStorage.setItem('theme', 'light');
            themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
        } else {
            document.documentElement.classList.add('dark-theme');
            localStorage.setItem('theme', 'dark');
            themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
        }
    });
    
    // Добавляем кнопку на страницу
    document.addEventListener('DOMContentLoaded', function() {
        document.body.appendChild(themeToggle);
    });
})();