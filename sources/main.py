"""
####################################################
#        #     #    ###     ####     ####          #
#        #     #   #   #    #   #    #   #         #
#         # # #    #   #    ####     #   #         #
#          # #      ###     #   #    ####          #
#                                                  #
#      ###      #   #    ####     ####   #####     #
#     #   #     #   #    #__     #         #       #
#     #   #     #   #    #        ####     #       #
#      ### #     ###     #####    ____#    #       #
####################################################

Author: Abel Haller, Hippolyte Pankutz

Main file of the application. It contains the main routes and the configuration of the application.

Imports:
    - flask: For handling the web application
    - flask_login: For handling the user sessions
    - flask_session: For handling the user sessions
    - flask_talisman: For adding security headers to the application
    - flask_wtf.csrf: For adding CSRF protection to the application
    
    - auth: The blueprint for the authentication routes
    - dashboard: The blueprint for the dashboard routes
    - create: The blueprint for the creation routes
    - quests: The blueprint for the quests routes
    - discover: The blueprint for the discover routes
    - user_data: The blueprint for the user data routes
    - emailing: The blueprint for the emailing routes
    - models: The User model
    - root: The root of the application
    - os: For handling the environment variables
    - datetime: For handling the date and time
"""

from flask import Flask, session, render_template, request
from flask_login import LoginManager, current_user, login_required
from flask_session import Session
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
import logging

from auth import auth_bp 
from dashboard import main_bp
from create import create_bp
from quests import quests_bp
from discover import discover_bp
from user_data import user_data_bp
from emailing import emailing_bp
from help import help_bp
from models import User
from root import *
import os
import datetime

app = Flask(__name__)
# Configuration of the application
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY') # Secret key for the application
app.config['SESSION_TYPE'] = 'filesystem' # Type of session
app.config['SESSION_FILE_DIR'] = '/tmp' # Directory for the session files (Value for google cloud)
app.config['SESSION_PERMANENT'] = True # Session is permanent - it will be stored until the user logs out
app.config['SESSION_REFRESH_EACH_REQUEST'] = False # Refresh the session each request

Session(app)

# Configuration of the login manager
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login' # The view to redirect to when the user is not logged in
login_manager.login_message = 'Vous devez vous connecter pour accéder à cette page.' # The message to display when the user is not logged in

# The logic to load a user from the database
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
            # User not found in the database, disconnect the user
            return None

        # Create a User object from the database result
        return User(user_id, result[1], result[2], result[4], result[3], result[8], True if result[6] == 1 else False, True if result[7] == 1 else False)
    except mysql.connector.Error as e:
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Security headers
talisman = Talisman(app)
# Content Security Policy
csp = {
    'default-src': [
        '\'self\'', 
        'https://fonts.googleapis.com',
        'https://fonts.gstatic.com',
        'https://www.google.com/recaptcha/',
        'https://www.gstatic.com/recaptcha/'
    ],
    'script-src': [
        '\'self\'',
        'https://www.google.com/recaptcha/',
        'https://www.gstatic.com/recaptcha/'
    ],
    'style-src': [
        '\'self\'',
        'https://fonts.googleapis.com',
        '\'unsafe-inline\'' # Low security, but necessary for the use of the library 'typeit'
    ],
    'img-src': [
        '*', # Super low security, but necessary for the use of the quiz game that looks for images on the web
        'data:'
    ],
    'frame-src': [
        'https://www.google.com/recaptcha/', 
        'https://recaptcha.google.com/recaptcha/'
    ],
    'form-action': [
        '\'self\''
    ],
    'frame-ancestors': [
        '\'self\''
    ],
    'media-src': [
        '\'self\''
    ]
}

# HTTP Strict Transport Security
hsts = {
    'max_age': 31536000,
    'include_subdomains': True
}
# Permissions policy
permissions_policy = {
    'geolocation': '\'none\'',
    'camera': '\'none\'',
    'microphone': '\'self\'', # Necessary for the use of the microphone in one of the games
    'fullscreen': '\'self\'',
    'payment': '\'none\''
}
# Add the headers to Talisman
talisman.force_https = True # Force the use of HTTPS
talisman.force_file_save = True # Force the use of HTTPS for file saving
talisman.x_xss_protection = True # Enable the XSS protection
talisman.session_cookie_secure = True # Secure the session cookie
talisman.session_cookie_samesite = 'Lax' # Set the SameSite attribute of the session cookie to Lax
talisman.frame_options_allow_from = 'https://www.google.com' # Allow the use of iframes from Google

# Add the headers to Talisman
talisman.content_security_policy = csp
talisman.strict_transport_security = hsts
talisman.permissions_policy = permissions_policy

# CSRF protection
csrf = CSRFProtect(app)

# Importation of blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(create_bp)
app.register_blueprint(quests_bp)
app.register_blueprint(discover_bp)
app.register_blueprint(user_data_bp)
app.register_blueprint(emailing_bp)
app.register_blueprint(help_bp)
csrf.exempt(emailing_bp) # Exempt the emailing blueprint from CSRF protection because it uses a POST request from an external source

# Importation of games blueprints
from games.hangman import hangman_bp
app.register_blueprint(hangman_bp)

from games.typefast import typefast_bp
app.register_blueprint(typefast_bp)

from games.quiz import quiz_bp
app.register_blueprint(quiz_bp)

from games.memory import memory_bp
app.register_blueprint(memory_bp)

from games.snake import snake_bp
app.register_blueprint(snake_bp)

from games.memowordrize import memowordrize_bp
app.register_blueprint(memowordrize_bp)

from games.fallingword import fallingword_bp
app.register_blueprint(fallingword_bp)

@app.route('/')
def index():
    user = None
    if current_user.is_authenticated:
        user = current_user.name
    return render_template('index.html', user = user)

@app.route('/privacy-policy')
def privacy_policy():
    user = None
    if current_user.is_authenticated:
        user = current_user.name
    return render_template('privacy-policy.html', user = user)

@app.route('/resources')
def resources():
    user = None
    if current_user.is_authenticated:
        user = current_user.name
    return render_template('resources.html', user = user)

@app.route('/contact')
def contact():
    user = None
    if current_user.is_authenticated:
        user = current_user.name
    return render_template('contact.html', user = user)

@app.route('/about')
def about():
    user = None
    if current_user.is_authenticated:
        user = current_user.name
    return render_template('about.html', user = user)

@app.route('/method')
def method():
    user = None
    if current_user.is_authenticated:
        user = current_user.name
    return render_template('method.html', user = user)

# Errors handling
@app.errorhandler(404)
def page_not_found(e):
    logging.error('Page not found: %s', (request.path))
    return render_template('errors/404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    logging.error('Forbidden: %s', (request.path))
    return render_template('errors/403.html'), 403

@app.errorhandler(500)
def internal_server_error(e):
    logging.error('Server error: %s', (request.path))
    return render_template('errors/500.html'), 500

@app.route('/dashboard/errors/500')
def error_500():
    return render_template('errors/500.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')