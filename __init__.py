from flask import Flask, session, render_template, request
from flask_login import LoginManager, current_user, login_required
from flask_session import Session

from auth import auth_bp 
from main import main_bp
from create import create_bp
from quests import quests_bp
from discover import discover_bp
from user_data import user_data_bp
from models import User
from root import *
import os
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
app.config['SESSION_PERMANENT'] = False

Session(app)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Vous devez vous connecter pour accéder à cette page.'

@login_manager.user_loader
def load_user(user_id):
    conn = None
    cursor = None
    try: 
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        if not result:
            return None

        return User(user_id, result[1], result[2], result[4], result[3], result[8], True if result[6] == 1 else False, True if result[7] == 1 else False)
    except mysql.connector.Error as e:
        print(e)
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(create_bp)
app.register_blueprint(quests_bp)
app.register_blueprint(discover_bp)
app.register_blueprint(user_data_bp)

# Importation of games blueprints
from games.hangman import hangman_bp
app.register_blueprint(hangman_bp)

from games.typefast import typefast_bp
app.register_blueprint(typefast_bp)

@app.route('/')
def index():
    user = None
    if current_user.is_authenticated:
        user = current_user.name
    return render_template('index.html', user = user)

# Save data from routes (time passed, arrived at, etc.)
@app.before_request
def before_request():
    if not request.path.startswith('/static') and current_user.is_authenticated:
        current_route = request.path
        if 'user_data' not in session:
            session['user_data'] = {
                'route': current_route, 
                'time': str(datetime.datetime.now())
            }
        if current_route != session['user_data']['route'] and session['user_data']['time'] != 0:
            conn = None
            cursor = None
            try:
                conn = create_connection()
                cursor = conn.cursor()
                arrived_at = datetime.datetime.strptime(session['user_data']['time'], '%Y-%m-%d %H:%M:%S.%f')
                time_passed = datetime.datetime.now() - arrived_at
                route = session['user_data']['route']
                
                # Convert time_passed to seconds
                time_passed = time_passed.total_seconds()
                cursor.execute("INSERT INTO routes_log (user_id, route, time_passed, created_at) VALUES (%s, %s, %s, %s)", (current_user.id, route, time_passed, arrived_at))
                
                
                conn.commit()
            except mysql.connector.Error as e:
                print(e)
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
            
            session['user_data']['route'] = current_route
            session['user_data']['time'] = str(datetime.datetime.now())

# Errors handling
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
