import psycopg2
from psycopg2 import pool
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    connection_pool = None

    @classmethod
    def initialize(cls):
        cls.connection_pool = pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )

    @classmethod
    def get_connection(cls):
        return cls.connection_pool.getconn()

    @classmethod
    def return_connection(cls, connection):
        cls.connection_pool.putconn(connection)

    @classmethod
    def close_all_connections(cls):
        cls.connection_pool.closeall()