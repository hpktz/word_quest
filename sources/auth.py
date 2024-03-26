"""
This module contains the routes and functions for user authentication.

Imports:
    - flask: For handling the HTTP requests and responses.
    - flask_login: For managing user authentication and sessions.
    - models: For the User class.
    - time: For handling time-related operations.
    - bcrypt: For hashing and verifying passwords.
    - pyotp: For generating and verifying time-based one-time passwords (TOTP).
    - re: For handling regular expressions.
    - random: For generating random numbers.
    - jwt: For encoding and decoding JSON Web Tokens (JWT).
    - profanity_detector: For detecting profanity in text.
    - root: For the create_connection function.
    - sendmails: For sending emails to users.
    - logging: For logging errors and debugging information.
    
Blueprints:
    - auth_bp: The Blueprint for the authentication routes.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, session, request, current_app
from flask_login import login_user, login_required, logout_user, current_user
from models import User  # Assurez-vous d'importer votre classe User appropriée

import time
import bcrypt
import pyotp
import re
import random
import jwt

from profanity import profanity_detector
from root import *
from sendmails import send_mail
import logging

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
"""
The Blueprint for the authentication routes.

Attributes:
    - auth_bp: The Blueprint for the authentication routes.
    
Routes:
    - /auth/login : To display the login page.
    - /auth/login (POST) : To handle the POST request for user login.
    - /auth/register : To display the registration page.
    - /auth/register (POST) : To handle the POST request for user registration.
    - /auth/2fa : To display the two-factor authentication (2FA) page.
    - /auth/2fa (POST) : To handle the POST request for the 2FA page.
    - /auth/2fa_sendCodeAgain : To send a new 2FA code to the user's email address.
    - /auth/logout : To log out the current user.
"""

@auth_bp.route('/login')
def login():
    """
    Displays the login page.

    Returns:
        flask.render_template: The 'auth/login.html' template.
    """
    # Check if the user is already authenticated
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    # Check if the user has already entered their email and password
    if "from_input" in session:
        email = session["from_input"][0]
        password = session["from_input"][1]
        session.pop("from_input")
        return render_template('auth/login.html', email=email, password=password)
    return render_template('auth/login.html')

@auth_bp.route('/login', methods=['POST'])
def login_post():
    """
    Handles the POST request for user login.
        
    This function checks the user's authentication status and the session data to determine the appropriate action.
    
    Args:
        email (str): The user's email address.
        password_input (str): The user's password.
    
    Returns:
        flask.redirect: A redirect response based on the authentication and session data.
            - /auth/login : If the user is already authenticated.
            - /auth/login : If the user has not entered their email and password.
            - /auth/login : If the user's email is not found in the database.
            - /auth/login : If the user's password is incorrect.
            - /auth/sys_2fa : If the user's email is found in the database and 2FA is required.
            - /auth/login : If there is an error connecting to the database.
    """
    
    # Check if the user is already authenticated
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Check if the user has already entered their email and password
    email = request.form.get('email')
    password_input = request.form.get('password')

    cursor = None
    
    # Check if their is a session for login_tries and 2fa
    if "login_tries" not in session:
        session["login_tries"] = {}
    if "2fa" not in session:
        session["2fa"] = {
            "id": None,
            "email": None,
            "code": None,
            "expires": None,
            "delay": 0,
            "trials": 0,
            "action": None,
            "secret_key": None,
            "totp": None,
        }

    conn = None 
    cursor = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        # Check if the user's email is found in the database
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        data = cursor.fetchone()

        if data:
            # Check if the user has tried to log in too many times
            if email in session["login_tries"]:
                if session["login_tries"][email]["trials"] >= 3:
                    # Check if the delay period has passed
                    if time.time() - session["login_tries"][email]["last"] < 60:
                        flash("Trop de tentatives de connexion, veuillez réessayer dans " + str(int(60 - (time.time() - session["login_tries"][email]["last"]))) + " secondes")
                        return redirect(url_for('auth.login'))
            
            # Check if their is a session for 2fa and if the user's email is not the same as the one in the session
            if session["2fa"]["email"] != email:
                # Check if the user's password is correct
                password = password_input.encode('utf-8')
                if bcrypt.checkpw(password, data[5].encode('utf-8')):
                    # Check if the user's account is activated
                    if data[11] == True:
                        # Check if 2FA is required
                        if data[6] == False:
                            user = User(data[0], data[1], data[2], data[4], data[3], data[8], True if data[6] == 1 else False, True if data[7] == 1 else False)
                            login_user(user, remember=True)
                            session.pop("login_tries")
                            return redirect(url_for('main.index'))
                        else:
                            # Generate a new 2FA secret key and send the code to the user's email
                            secret_key = pyotp.random_base32()
                            totp = pyotp.TOTP(secret_key)
                            session["2fa"]["id"] = data[0]
                            session["2fa"]["email"] = email
                            session["2fa"]["action"] = "login"
                            session["2fa"]["secret_key"] = secret_key
                            session["2fa"]["expires"] = time.time() + 300
                            session["2fa"]["delay"] =  time.time() + 300
                            
                            # Send the 2FA code to the user's email
                            html = render_template('emails/2fa.html', name=data[1], code=totp.now())
                            send_mail(email, "Code de vérification - WORD QUEST", html)
                            return redirect(url_for('auth.sys_2fa'))
                    else:
                        session["from_input"] = [email, password_input]
                        flash("Votre compte n'est pas activé")
                        return redirect(url_for('auth.login'))
                else:
                    if email in session["login_tries"]:
                        session["login_tries"][email]["trials"] += 1
                        session["login_tries"][email]["last"] = time.time()
                    else:
                        session["login_tries"][email] = {
                            "trials": 1,
                            "last": time.time()
                        }
                    session["from_input"] = [email, password_input]
                    flash("Mot de passe incorrect")
                    return redirect(url_for('auth.login'))
            else:
                return redirect(url_for('auth.sys_2fa'))
        else:
            session["from_input"] = [email, password_input]
            flash("Email incorrect")
            return redirect(url_for('auth.login'))
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error("Error connecting to database: " + str(e))
        session["from_input"] = [email, password_input]
        flash('Erreur de connexion')
        return redirect(url_for('auth.login'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@auth_bp.route('/register')
def register():
    """
    Renders the registration page if the user is not authenticated.
    
    Returns:
        flask.render_template: The 'auth/register.html' template.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    return render_template('auth/register.html')


@auth_bp.route('/register', methods=['POST'])
def register_post():
    """
    Handles the POST request for user registration.
    
    This function checks the user's authentication status and the session data to determine the appropriate action.
    
    Args:
        name (str): The user's name.
        birthday (str): The user's birthday.
        email (str): The user's email address.
        password_input (str): The user's password.
        picture (str): The user's profile picture.
        
    Returns:
        flask.redirect: A redirect response based on the authentication and session data.
            - /dashboard : If the user is already authenticated.
            - /auth/register : If the user's email is already in use.
            - /auth/register : If the user's email is invalid.
            - /auth/register : If the user's birthday is invalid.
            - /auth/register : If there is an error connecting to the database.
            - /auth/sys_2fa : If the user's email is not in the session.
            - /auth/sys_2fa : If the user's email is in the session.
    """
    
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    else:
        name = request.form.get('name')
        birthday = request.form.get('birthday')
        email = request.form.get('email')
        password_input = request.form.get('password')
        picture = request.form.get('profile-picture')
        if not picture:
            picture = 0

        if "login_tries" not in session:
            session["login_tries"] = {}
        if "2fa" not in session:
            session["2fa"] = {
                "id": None,
                "email": None,
                "code": None,
                "expires": None,
                "delay": 0,
                "trials": 0,
                "action": None,
                "secret_key": None,
                "totp": None,
            }

        conn = None
        cursor = None
        try:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM users WHERE email='{email}'")
            data = cursor.fetchone()

            # Check if the user's email is already in use
            if data and data[11] == True:
                flash("Email déjà utilisé")
                return redirect(url_for('auth.register'))
            else:
                if session["2fa"] is None or session["2fa"]["email"] != email:
                    # Check if the user's email is invalid
                    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                        flash("Email invalide")
                        return redirect(url_for('auth.register'))
                    
                    if profanity_detector(name):
                        flash("Nom invalide - Veuillez ne pas utiliser de mots inappropriés")
                        return redirect(url_for('auth.register'))

                    # Hash the user's password
                    password = password_input.encode('utf-8')
                    hashed = bcrypt.hashpw(password, bcrypt.gensalt())

                    # Check if the user's birthday is invalid
                    birthday_pattern = re.compile(r"\d{4}-\d{2}-\d{2}")
                    if not birthday_pattern.match(birthday):
                        flash("Date de naissance invalide")
                        return redirect(url_for('auth.register'))

                    # Check if the user's profile picture is invalid
                    picture = int(picture)
                    if picture > 12 or picture < 1:
                        picture = random.randint(1, 12)
                    picture = f"picture-{picture}"
                    
                    if data:
                        cursor.execute("UPDATE users SET name=%s, birthday=%s, picture=%s, password=%s WHERE email=%s", (name, birthday, picture, hashed, email))
                    else:
                        # Insert the user's data into the database
                        cursor.execute("INSERT INTO users (name, birthday, email, picture, password) VALUES (%s, %s, %s, %s, %s)", (name, birthday, email, picture, hashed))
                        user_id = cursor.lastrowid
                        # Insert the user's default data into the database
                        cursor.execute("INSERT INTO user_statements (user_id, transaction_type, transaction) VALUES (%s, %s, %s),(%s, %s, %s)", (user_id,"gems",200,user_id,"lives",5))

                    # Generate a new 2FA secret key and send the code to the user's email
                    secret_key = pyotp.random_base32()
                    totp = pyotp.TOTP(secret_key)
                    session["2fa"]["id"] = None
                    session["2fa"]["email"] = email
                    session["2fa"]["action"] = "register"
                    session["2fa"]["secret_key"] = secret_key
                    session["2fa"]["expires"] = time.time() + 300
                    session["2fa"]["delay"] =  time.time() + 300
                    
                    # Send the 2FA code to the user's email
                    html = render_template('emails/2fa.html', name=name, code=totp.now())
                    send_mail(email, "Code de vérification - WORD QUEST", html)
                    return redirect(url_for('auth.sys_2fa'))
                else:
                    return redirect(url_for('auth.sys_2fa'))
        except Exception as e:
            if conn:
                conn.rollback()
            logging.error("Error connecting to database: " + str(e))
            flash('Erreur de connexion')
            return redirect(url_for('auth.register'))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

@auth_bp.route('/2fa')
def sys_2fa():
    """
    Displays the two-factor authentication (2FA) page.
    
    Returns:
        flask.render_template: The 'auth/2fa.html' template.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if "2fa" not in session or session["2fa"]["email"] == None:
        return redirect(url_for('auth.login'))
    return render_template('auth/2fa.html')

@auth_bp.route('/2fa_sendCodeAgain')
def sys_2fa_sendCodeAgain():
    """
    Sends a new 2FA code to the user's email address.
    
    Returns:
        flask.redirect: A redirect response based on the 2FA session data.
            - /dashboard : If the user is already authenticated.
            - /auth/login : If the 2FA session does not have an email set.
            - /auth/2fa : If the delay period has not passed.
            - /auth/2fa : If the code has been sent successfully.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if session["2fa"]["email"] == None:
        return redirect(url_for('auth.login'))
    if time.time() > session["2fa"]["delay"]:
        # Generate a new 2FA secret key and send the code to the user's email
        secret_key = pyotp.random_base32()
        totp = pyotp.TOTP(secret_key)
        session["2fa"]["trials"] = 0
        session["2fa"]["secret_key"] = secret_key
        session["2fa"]["expires"] = time.time() + 300
        session["2fa"]["delay"] =  time.time() + 300

        html = render_template('emails/2fa.html', name="", code=totp.now())
        send_mail(session["2fa"]["email"], "Code de vérification - WORD QUEST", html)
        flash("Nouveau code envoyé")
        return redirect(url_for('auth.sys_2fa'))
    else:
        flash("Vous devez attendre " + str(int(session["2fa"]["delay"] - time.time())) + " secondes avant de pouvoir envoyer un nouveau code")
        return redirect(url_for('auth.sys_2fa'))


@auth_bp.route('/2fa', methods=['POST'])
def sys_2fa_post():
    """
    Handle the POST request for the two-factor authentication (2FA) page.

    Args:
        code (str): The 2FA code entered by the user.
    
    Returns:
        flask.redirect: A redirect response based on the 2FA session data.
            - /dashboard : If the user is already authenticated.
            - /dashboard : If the 2FA code is correct.
            - /auth/2fa : If the 2FA code is incorrect.
            - /auth/2fa : If the 2FA code has expired.
            - /auth/2fa : If the user has tried to log in too many times.
            - auth/login : If the user is not authenticated.
    """
    def _login(user_id):
        """
        Log in the user.

        Args:
            user_id (int): The user's ID.

        Returns:
            flask.redirect: A redirect response to the dashboard.
        """
        # Log in the user
        conn = None
        cursor = None
        try:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
            data = cursor.fetchone()
            user = User(data[0], data[1], data[2], data[4], data[3], data[8], True if data[6] == 1 else False, True if data[7] == 1 else False)
            login_user(user, remember=True)
            session.pop("login_tries")
            session.pop("2fa")
            return redirect(url_for('main.index'))
        except Exception as e:
            if conn:
                conn.rollback()
            logging.error("Error connecting to database: " + str(e))
            flash('Une erreur est survenue lors de la connexion')
            return redirect(url_for('auth.login'))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def _register(email):
        """
        Activate the user's account and log in the user.

        Args:
            email (str): The user's email address.

        Returns:
            flask.redirect: A redirect response to the dashboard.
        """
        conn = None
        cursor = None
        try:
            conn = create_connection()
            cursor = conn.cursor()
            
            # Activate the user's account
            cursor.execute("UPDATE users SET activated=TRUE WHERE email=%s", (email,))
            cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
            data = cursor.fetchone()
            user = User(data[0], data[1], data[2], data[4], data[3], data[8], True if data[6] == 1 else False, True if data[7] == 1 else False)
            login_user(user, remember=True)
            session.pop("login_tries")
            session.pop("2fa")
            return redirect(url_for('help.index'))
        except Exception as e:
            if conn:
                conn.rollback()
            logging.error("Error connecting to database: " + str(e))
            flash('Une erreur est survenue lors de l\'activation de votre compte')
            return redirect(url_for('auth.register'))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    # Check if the user is already authenticated
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Check if the 2FA session has an email set
    if session["2fa"]["email"] == None:
        return redirect(url_for('auth.login'))
    
    # Check if the 2FA code is correct
    code = request.form.get('code')
    if not code:
        flash("Code incorrect")
        return redirect(url_for('auth.sys_2fa'))
    
    # Check if the 2FA code has expired
    if time.time() > session["2fa"]["expires"]:
        flash("Code expiré")
        return redirect(url_for('auth.sys_2fa'))
    
    # Check if the user has tried to log in too many times
    if session["2fa"]["trials"] >= 3 and session["2fa"]["delay"] > time.time():
        flash("Trop de tentatives de connexion, veuillez réessayer dans " + str(int(session["2fa"]["delay"] - time.time())) + " secondes")
        return redirect(url_for('auth.sys_2fa'))
    elif pyotp.TOTP(session["2fa"]["secret_key"]).verify(code, valid_window=10): # Check if the 2FA code is correct
        if session["2fa"]["action"] == "login":
            return _login(session["2fa"]["id"])
        elif session["2fa"]["action"] == "register":
            return _register(session["2fa"]["email"])
    else:
        # Increment the number of 2FA trials
        session["2fa"]["trials"] += 1
        if session["2fa"]["trials"] >= 3:
            if session["2fa"]["delay"] < time.time():
                session["2fa"]["delay"] = time.time() + 30 * session["2fa"]["trials"]
            flash("Trop de tentatives de connexion, veuillez réessayer dans " + str(int(session["2fa"]["delay"] - time.time())) + " secondes")
            return redirect(url_for('auth.sys_2fa'))
        flash("Code incorrect")
        return redirect(url_for('auth.sys_2fa'))

@auth_bp.route('/logout')
@login_required
def logout():
    """
    Log out the current user.

    Returns:
        A redirect response to the login page.
    """
    session.clear()
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/pass-recovery')
def pass_recovery():
    """
    Displays the password recovery page.

    Returns:
        flask.render_template: The 'auth/pass-recovery.html' template.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    return render_template('auth/password-recovery.html')

@auth_bp.route('/pass-recovery/send-link', methods=['POST'])
def pass_recovery_send_link():
    """
    Sends a password recovery link to the user's email address.

    Args:
        email (str): The user's email address.

    Returns:
        flask.redirect: A redirect response based on the email address.
            - /auth/pass-recovery : If the user is already authenticated.
            - /auth/pass-recovery : If the user's email is not found in the database.
            - /auth/pass-recovery : If there is an error connecting to the database.
            - /auth/pass-recovery : If the password recovery link has been sent successfully.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    email = request.form.get('email')
    conn = None
    cursor = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        data = cursor.fetchone()
        # Check if the user's email is found in the database
        if data:
            actual_token = data[12] # Check if a password recovery email has already been sent
            if actual_token and actual_token > datetime.datetime.utcnow():
                flash("Un email de récupération de mot de passe a déjà été envoyé")
                return redirect(url_for('auth.pass_recovery'))
            
            # Otherwise, generate a new password recovery token and send the link to the user's email
            token = jwt.encode({'email': email, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, current_app.config['SECRET_KEY'], algorithm="HS256")
            url = request.host_url + "auth/pass-recovery/reset-password/" + token # Generate the password recovery link
            send_mail(email, "Récupération de mot de passe - WORD QUEST", render_template('emails/password-recovery.html', url=url)) # Send the password recovery link to the user's email
            flash("Un email de récupération de mot de passe a été envoyé")
            return redirect(url_for('auth.pass_recovery'))
        else:
            flash("Email introuvable")
            return redirect(url_for('auth.pass_recovery'))
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error("Error connecting to database: " + str(e))
        flash('Erreur de connexion')
        return redirect(url_for('auth.pass_recovery'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@auth_bp.route('/pass-recovery/reset-password/<token>')
def pass_recovery_reset_password(token):
    """
    Displays the password reset page.

    Args:
        token (str): The password recovery token.

    Returns:
        flask.render_template: The 'auth/password-reset.html' template.
    """
    if current_user.is_authenticated:
        session.clear()
        logout_user()
    try:
        # Decode the password recovery token
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        if datetime.datetime.fromtimestamp(payload["exp"]) > datetime.datetime.utcnow(): # Check if the token has expired
            return render_template('auth/password-reset.html', token=token) # Render the password reset page
        else:
            flash("Le lien a expiré")
            return redirect(url_for('auth.pass_recovery'))
    except Exception as e:
        logging.error("Error decoding token: " + str(e))
        flash("Le lien est invalide")
        return redirect(url_for('auth.pass_recovery'))
    
@auth_bp.route('/pass-recovery/reset-password/<token>', methods=['POST'])
def pass_recovery_reset_password_post(token):
    """
    Handles the POST request for password reset.

    Args:
        token (str): The password recovery token.
        password (str): The new password.

    Returns:
        flask.redirect: A redirect response based on the password recovery token.
            - /auth/pass-recovery/reset-password/<token> : If the password recovery token is invalid.
            - /auth/login : If the password has been reset successfully.
            - /auth/pass-recovery/reset-password/<token> : If there is an error connecting to the database.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    password = request.form.get('password')
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        # Check if the token has expired
        if datetime.datetime.fromtimestamp(payload["exp"]) > datetime.datetime.utcnow():
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email=%s", (payload["email"],))
            data = cursor.fetchone()
            if data:
                password = password.encode('utf-8')
                hashed = bcrypt.hashpw(password, bcrypt.gensalt())
                cursor.execute("UPDATE users SET password=%s, password_recovery_session=NULL WHERE email=%s", (hashed, payload["email"])) # Update the user's password
                conn.commit()
                flash("Mot de passe modifié avec succès")
                return redirect(url_for('auth.login'))
            else:
                flash("Email introuvable")
                return redirect(url_for('auth.pass_recovery'))
        else:
            flash("Le lien a expiré")
            return redirect(url_for('auth.pass_recovery'))
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error("Error connecting to database: " + str(e))
        flash('Erreur de connexion')
        return redirect(url_for('auth.pass_recovery'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()