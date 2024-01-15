import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()

_dbserver = os.getenv('DB_HOST')
_dbuser = os.getenv('DB_USERNAME')
_dbpass = os.getenv('DB_PASSWORD')
_dbname = os.getenv('DB_NAME')


class create_connection:
    def __init__(self):
        self.conn = mysql.connector.connect(host=_dbserver, database=_dbname, user=_dbuser, password=_dbpass)
        self.cursor = None
    def __enter__(self):
        return self.conn
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
    def cursor(self):
        return self.conn.cursor()
    def close(self):
        self.conn.close()

def close_connection(conn):
    if conn:
        conn.close()

def valiData(data):
    data = data.strip()
    data = data.replace("'", "''")
    data = data.replace('"', '""')
    return data