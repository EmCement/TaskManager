import asyncio
from database import init_db, close_db
from models import Priority, Status


async def init_base_data():
    """Инициализация базовых приоритетов и статусов"""
    await init_db()

    try:
        priorities_count = await Priority.all().count()
        if priorities_count == 0:
            await Priority.create(name="Низкий", level=1, color="#95a5a6")
            await Priority.create(name="Средний", level=2, color="#f39c12")
            await Priority.create(name="Высокий", level=3, color="#e74c3c")
            await Priority.create(name="Критический", level=4, color="#c0392b")
            print("Созданы приоритеты")

        statuses_count = await Status.all().count()
        if statuses_count == 0:
            await Status.create(name="Новая", order_num=1, is_final=False)
            await Status.create(name="В работе", order_num=2, is_final=False)
            await Status.create(name="На проверке", order_num=3, is_final=False)
            await Status.create(name="Завершена", order_num=4, is_final=True)
            await Status.create(name="Отменена", order_num=5, is_final=True)
            print("Созданы статусы")

    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(init_base_data())
