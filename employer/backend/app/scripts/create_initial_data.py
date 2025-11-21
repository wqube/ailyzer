# scripts/create_initial_data.py
"""
Скрипт для создания начальных данных в БД (роли).

Запуск:
    python -m scripts.create_initial_data
"""

import asyncio
from sqlalchemy import select

from shared.db.session import db_helper
from shared.db.models import Role


async def create_roles():
    """Создаёт базовые роли в БД"""
    
    async with db_helper.AsyncSessionLocal() as session:
        # Проверяем, есть ли роли
        result = await session.execute(select(Role))
        existing_roles = result.scalars().all()
        
        if existing_roles:
            print("✅ Роли уже существуют в БД:")
            for role in existing_roles:
                print(f"   - {role.role_id}: {role.name}")
            return
        
        # Создаём роли
        roles = [
            Role(role_id=1, name="candidate"),   # Кандидат
            Role(role_id=2, name="employer"),    # Работодатель
            Role(role_id=3, name="admin"),       # Администратор
        ]
        
        session.add_all(roles)
        await session.commit()
        
        print("✅ Роли успешно созданы:")
        for role in roles:
            print(f"   - {role.role_id}: {role.name}")


async def main():
    """Главная функция"""
    print("🚀 Создание начальных данных...\n")
    
    try:
        await create_roles()
        print("\n✅ Все данные успешно созданы!")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
    finally:
        await db_helper.engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
