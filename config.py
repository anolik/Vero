import os
from dotenv import load_dotenv

load_dotenv()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme")
TOKEN_EXPIRY_DAYS = int(os.getenv("TOKEN_EXPIRY_DAYS", "30"))
DATABASE_PATH = os.getenv("DATABASE_PATH", "vero.db")
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key-in-production")
