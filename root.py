"""
This module contains the root functions for the application.


Imports:
    - mysql.connector: MySQL connector for Python.
    - Error: Error class from mysql.connector.
    - load_dotenv: Load environment variables from .env file.
    - os: Miscellaneous operating system interfaces.

Functions:
    - create_connection: Create a connection to the database.
    - close_connection: Close a connection to the database.
    - valiData: Validate data to prevent SQL injection.
"""

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import datetime
import locale

# Load environment variables from .env file
load_dotenv()

_dbserver = os.getenv('DB_HOST')
_dbuser = os.getenv('DB_USERNAME')
_dbpass = os.getenv('DB_PASSWORD')
_dbname = os.getenv('DB_NAME')

# Create a connection to the database
def create_connection() -> mysql.connector.connection.MySQLConnection:
    conn = mysql.connector.connect(host=_dbserver, database=_dbname, user=_dbuser, password=_dbpass)
    conn.time_zone = '+01:00'
    return conn

# Close a connection to the database
def close_connection(conn: mysql.connector.connection.MySQLConnection) -> None:
    if conn:
        conn.close()

# Validate data to prevent SQL injection
def valiData(data: str) -> str:
    """
    Validate data to prevent SQL injection.

    Args:
        data (string): The data to validate.

    Returns:
        string: The validated data.
    """
    data = data.strip()
    data = data.replace("'", "''")
    data = data.replace('"', '""')
    return data

def convert_date(date: datetime) -> str:
    """
    Convert a datetime object to a string in the format 'dd month yyyy'.
    """
    print(date)
    months = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
    return f"{date.day} {months[date.month - 1]} {date.year}"