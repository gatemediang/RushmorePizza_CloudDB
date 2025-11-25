import os
import psycopg2


class MissingPasswordError(RuntimeError):
    pass


def connect():
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = int(os.getenv("DB_PORT", "5432"))
    db = os.getenv("DB_NAME", "rushmore_db")
    user = os.getenv("DB_USER", "postgres")
    pwd = os.getenv("DB_PASSWORD", "")
    ssl = os.getenv("SSL_MODE", "disable")
    if not pwd:
        raise MissingPasswordError("DB_PASSWORD environment variable is empty.")
    return psycopg2.connect(
        host=host, port=port, dbname=db, user=user, password=pwd, sslmode=ssl
    )
