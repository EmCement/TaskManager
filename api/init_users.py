import asyncio

from crud import get_user_by_username, create_user
from database import init_db, close_db
from schemas import UserCreate


async def init_test_users():
    test_users = [
        {
            "username": "admin",
            "email": "admin@example.com",
            "password": "password123",
            "full_name": "Admin User",
            "role": "admin"
        }
    ]

    await init_db()

    try:
        for user_data in test_users:
            existing_user = await get_user_by_username(user_data["username"])
            if existing_user:
                print(f"Пользователь {user_data['username']} уже существует")
                continue

            user_create = UserCreate(**user_data)
            await create_user(user=user_create)
            print(f"Создан пользователь {user_data['username']} ({user_data['role']})")

    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(init_test_users())
