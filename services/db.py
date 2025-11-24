import os
import psycopg2


class MissingPasswordError(RuntimeError):
    pass


def connect():
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = int(os.getenv("DB_PORT", "5432"))
    db = os.getenv("DB_NAME", "rushmore_db")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "")
    sslmode = os.getenv("SSL_MODE", "prefer")  # Change default to 'prefer'

    if not password:
        raise MissingPasswordError("DB_PASSWORD environment variable is empty.")

    return psycopg2.connect(
        host=host, port=port, dbname=db, user=user, password=password, sslmode=sslmode
    )
