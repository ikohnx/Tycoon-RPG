import os
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

_connection_pool = None

def init_connection_pool():
    """Initialize the connection pool with error handling."""
    global _connection_pool
    if _connection_pool is None:
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is not set")
        try:
            _connection_pool = pool.ThreadedConnectionPool(
                minconn=2,
                maxconn=20,
                dsn=database_url
            )
        except Exception as e:
            print(f"Failed to create connection pool: {e}")
            raise
    return _connection_pool


def get_connection():
    """Get a database connection from the pool."""
    global _connection_pool
    
    if _connection_pool is None:
        init_connection_pool()
    
    try:
        conn = _connection_pool.getconn()
        conn.cursor_factory = RealDictCursor
        return conn
    except pool.PoolError:
        database_url = os.environ.get("DATABASE_URL")
        return psycopg2.connect(database_url, cursor_factory=RealDictCursor)


def return_connection(conn):
    """Return a connection to the pool."""
    global _connection_pool
    if _connection_pool is not None and conn is not None:
        try:
            _connection_pool.putconn(conn)
        except Exception:
            try:
                conn.close()
            except Exception:
                pass


@contextmanager
def db_cursor(commit_on_success=False):
    """Context manager for safe database access with automatic cleanup.
    
    Usage:
        with db_cursor() as (conn, cur):
            cur.execute("SELECT * FROM table")
            result = cur.fetchall()
        
        with db_cursor(commit_on_success=True) as (conn, cur):
            cur.execute("INSERT INTO table VALUES (%s)", (value,))
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        yield conn, cur
        if commit_on_success:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        return_connection(conn)
