# test_conn.py
import psycopg2, sys, os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "5434")),  # default to local service
        dbname=os.getenv("DB_NAME", "rushmore_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        sslmode=os.getenv("SSL_MODE", "disable"),
        connect_timeout=5,
    )
    with conn.cursor() as cur:
        cur.execute("SELECT version(), current_setting('port')")
        print(cur.fetchone())
    print("OK - TCP connection succeeded")
    conn.close()
except Exception as e:
    print("FAIL - exception:", repr(e))
    sys.exit(1)
