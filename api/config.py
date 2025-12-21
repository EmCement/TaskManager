import os

SECRET_KEY = os.getenv("SECRET_KEY", "test-key-lolollololollolololololololoolololololololololo")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

DATABASE_URL = os.getenv("DATABASE_URL", "postgres://taskuser:taskpassword@localhost:5432/taskmanager")
