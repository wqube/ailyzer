# api/routers/__init__.py
"""Главный роутер приложения"""

from fastapi import APIRouter

# Импортируем роутеры
from api.routers.user import router as user_router
from api.routers.vacancy import router as vacancy_router
from api.routers.role import router as role_router
from api.routers.auth import router as auth_router  # 👈 НОВЫЙ роутер
from api.routers.candidates import router as candidates_router

# Демо-роутеры (можно оставить для тестирования)
# from api.routers.demo_auth.views import router as demo_auth_router
# from api.routers.demo_auth.demo_jwt_auth import router as demo_auth_jwt_router

# Главный роутер
router = APIRouter()

# 👇 ОСНОВНЫЕ роутеры (порядок важен!)
router.include_router(auth_router)      # /api/v1/auth/*
router.include_router(vacancy_router)   # /api/v1/vacancies/*
router.include_router(user_router)      # /api/v1/users/*
router.include_router(role_router)      # /api/v1/role/*
router.include_router(candidates_router) 
# 👇 ДЕМО роутеры (для тестирования, можно удалить в проде)
# demo_auth_router.include_router(demo_auth_jwt_router)
# router.include_router(demo_auth_router)  # /api/v1/demo_auth/*