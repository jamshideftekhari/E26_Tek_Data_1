from mysql.connector import pooling

from config import DB_CONFIG

_pool = pooling.MySQLConnectionPool(
    pool_name="elective_registration_pool",
    pool_size=5,
    **DB_CONFIG,
)


def get_connection():
    return _pool.get_connection()
