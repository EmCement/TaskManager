from tortoise import Tortoise
import config

TORTOISE_ORM = {
    "connections": {
        "default": config.DATABASE_URL
    },
    "apps": {
        "models": {
            "models": ["models", "aerich.models"],
            "default_connection": "default",
        },
    },
    "use_tz": True,
}


async def init_db():
    """Инициализация подключения к базе данных"""
    await Tortoise.init(config=TORTOISE_ORM)
    # Генерация схем
    # await Tortoise.generate_schemas()


async def close_db():
    """Закрытие подключения к базе данных"""
    await Tortoise.close_connections()
