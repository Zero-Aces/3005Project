import psycopg2
from contextlib import contextmanager
import logging

class HealthClubDatabase:
    _instance = None  # This will hold the single instance

    def __new__(cls, dbname="Tester", user="postgres", password="postgres", host='localhost'):
        if cls._instance is None:
            cls._instance = super(HealthClubDatabase, cls).__new__(cls)
            cls._instance.connection_params = {
                'dbname': dbname,
                'user': user,
                'password': password,
                'host': host
            }
            cls._instance.connection = None
            cls._instance.connect()
        return cls._instance

    def connect(self):
        try:
            self.connection = psycopg2.connect(**self.connection_params)
            self.connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        except Exception as e:
            logging.error(f"Failed to connect to the database due to: {e}")

    @contextmanager
    def get_connection(self):
        if self.connection is None or self.connection.closed:
            self.connect()
        try:
            yield self.connection
        except Exception as e:
            logging.error(f"Failed to connect to the database due to: {e}")

    def execute_query(self, query, params=None, fetch=False):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                if fetch:
                    return cur.fetchall()
                else:
                    return cur.statusmessage
