import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()

_dbserver = os.getenv('DB_HOST')
_dbuser = os.getenv('DB_USERNAME')
_dbpass = os.getenv('DB_PASSWORD')
_dbname = os.getenv('DB_NAME')

def create_connection():
    conn = mysql.connector.connect(host=_dbserver, database=_dbname, user=_dbuser, password=_dbpass)
    return conn

def close_connection(conn):
    if conn:
        conn.close()

def valiData(data):
    data = data.strip()
    data = data.replace("'", "''")
    data = data.replace('"', '""')
    return data