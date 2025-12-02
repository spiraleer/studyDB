# routes/dashboard.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Инициализируем шаблоны
templates = Jinja2Templates(directory="templates")

# Инициализируем роутер
router = APIRouter(
    tags=["Панель управления"],
)

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """
    Роут для отображения базовой страницы панели управления.
    """
    return templates.TemplateResponse(
        "dashboard.html", 
        {"request": request}
    )