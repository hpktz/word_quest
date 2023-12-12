from flask import Flask, jsonify, request
from flask_cors import CROS
import mysql.connector
from mysql.connector import Error
from ../var import *

conn = mysql.connector.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASS
)

class Account:
    def __init__(self):
        self._userData = {
            'id': None,
            'name': None,
            'birthday': None,
            'lvl': None,
            'email': None,
            'password': None,
            '2fa': None,
            'ban': None,
            'ban_reason': None,
            'ban_count': None,
            'active': None
        }
        self._isLogin = False
    def _login(self, email, password):
        if self._isLogin():
            return jsonify({'code': 400, 'message': 'Already logged in', 'mess_code': 'already_logged_in'})
    def _logout(self):
        pass
    def _2fa(self):
        pass
    def _2faSend(self):
        pass
    def _isLogin(self):
        pass

app = Flask(__name__)
CORS(app)

@app.route('/auth/check', methods=['GET'])