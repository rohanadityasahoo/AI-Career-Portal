import os

from dotenv import load_dotenv

load_dotenv()

# Railway provides MYSQLHOST, MYSQLPORT, MYSQLUSER,
# MYSQLPASSWORD and MYSQLDATABASE.
# Local development can use the MYSQL_HOST-style names
# from .env.

MYSQL_HOST = os.getenv(
    "MYSQLHOST",
    os.getenv("MYSQL_HOST", "localhost")
)

MYSQL_PORT = int(
    os.getenv(
        "MYSQLPORT",
        os.getenv("MYSQL_PORT", "3306")
    )
)

MYSQL_USER = os.getenv(
    "MYSQLUSER",
    os.getenv("MYSQL_USER", "root")
)

MYSQL_PASSWORD = os.getenv(
    "MYSQLPASSWORD",
    os.getenv("MYSQL_PASSWORD", "")
)

MYSQL_DB = os.getenv(
    "MYSQLDATABASE",
    os.getenv("MYSQL_DB", "careerpilot_ai")
)

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "").strip().lower()
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
