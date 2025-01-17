# SQLite configuration
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_FILE_PATH = f"{os.path.join(BASE_DIR, 'db', 'books.db')}"
SQLITE_DB_URL = f"sqlite:///{SQLITE_FILE_PATH}"

# JWT configuration
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# first superuser configuration
FIRST_ADMIN_USER_EMAIL = "root@test.com"
FIRST_ADMIN_USER_PASSWORD = "admin"
