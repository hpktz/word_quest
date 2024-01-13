from flask import Flask, session
from flask_login import LoginManager, current_user
from flask_session import Session

from auth import auth_bp  # Importez votre blueprint depuis le fichier account.py
from main import main_bp  # Importez votre blueprint depuis le fichier home.py
from create import create_bp
from quests import quests_bp
from discover import discover_bp
from models import User  # Assurez-vous d'importer votre classe User appropriée
from root import *
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
app.config['SESSION_PERMANENT'] = False

Session(app)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    cursor = None
    conn = None
    try: 
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        if not result:
            return None
        return User(user_id)
    except mysql.connector.Error as e:
        print(e)
        return None
    finally:
        if cursor:
            cursor.close()
        close_connection(conn)

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(create_bp)
app.register_blueprint(quests_bp)
app.register_blueprint(discover_bp)


# Importation of games blueprints
from games.hangman import hangman_bp
app.register_blueprint(hangman_bp)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        pass

if __name__ == '__main__':
    app.run(debug=True)
