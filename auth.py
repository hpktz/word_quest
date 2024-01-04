from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from flask_login import login_user, login_required, logout_user, current_user
from models import User  # Assurez-vous d'importer votre classe User appropriée

import time
import bcrypt
import pyotp
import re

from root import *
from sendmails import send_mail

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login')
def login():
    """
    Displays the login page.

    If the user is already authenticated, they are redirected to the home page.
    If login data is stored in the session, it is retrieved and displayed in the login form.
    Otherwise, the login page is displayed without any pre-filled data.

    :return: The HTML template of the login page.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
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

    This function checks if the user is already authenticated. If not, it retrieves the email and password from the request form.
    It then checks if the email exists in the database and if the password matches the hashed password stored in the database.
    If the email exists and the password is correct, it checks if the user has enabled two-factor authentication (2FA).
    If 2FA is enabled, it generates a random secret key and a time-based one-time password (TOTP) using the secret key.
    It sends the TOTP code to the user's email and redirects to the 2FA verification page.
    If 2FA is not enabled, it logs in the user and redirects to the main index page.
    If the email does not exist, it displays an error message.
    If the password is incorrect, it increments the login trials counter and displays an error message.
    If there are too many login trials within a certain time frame, it displays an error message and blocks login attempts for a specific period.
    If there is an error connecting to the database, it displays an error message.

    Returns:
        A redirect response to the appropriate page based on the login process.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    email = request.form.get('email')
    password_input = request.form.get('password')

    cursor = None
    
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
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        data = cursor.fetchone()

        if data:
            if email in session["login_tries"]:
                if session["login_tries"][email]["trials"] >= 3:
                    # Affiche le message d'erreur et le temps restant
                    if time.time() - session["login_tries"][email]["last"] < 60:
                        flash("Trop de tentatives de connexion, veuillez réessayer dans " + str(int(60 - (time.time() - session["login_tries"][email]["last"]))) + " secondes")
                        return redirect(url_for('auth.login'))
            if session["2fa"]["email"] != email:
                password = password_input.encode('utf-8')
                if bcrypt.checkpw(password, data[8].encode('utf-8')):
                    if data[12] == True:
                        if data[9] == False:
                            user = User(data[0])
                            login_user(user)
                            session.pop("login_tries")
                            return redirect(url_for('main.index'))
                        else:
                            secret_key = pyotp.random_base32()
                            totp = pyotp.TOTP(secret_key, interval=120)
                            session["2fa"]["id"] = data[0]
                            session["2fa"]["email"] = email
                            session["2fa"]["code"] = totp.now()
                            session["2fa"]["action"] = "login"
                            session["2fa"]["secret_key"] = secret_key
                            session["2fa"]["totp"] = totp
                            session["2fa"]["expires"] = time.time() + 60
                            session["2fa"]["delay"] =  time.time() + 60
                            send_mail(email, "2FA code", f"Your 2FA code is: {session['2fa']['code']}")
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
    except mysql.connector.Error as e:
        session["from_input"] = [email, password_input]
        flash('Erreur de connexion')
        return redirect(url_for('auth.login'))
    finally:
        if cursor:
            cursor.close()
        close_connection(conn)

@auth_bp.route('/register')
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    return render_template('auth/register.html')


@auth_bp.route('/register', methods=['POST'])
def register_post():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    else:
        name = request.form.get('name')
        birthday = request.form.get('birthday')
        email = request.form.get('email')
        password_input = request.form.get('password')

        cursor = None
        
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

            if data and data[12] == True:
                flash("Email déjà utilisé")
                return redirect(url_for('auth.register'))
            else:
                if session["2fa"]["email"] != email:
                    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                        flash("Email invalide")
                        return redirect(url_for('auth.register'))
                    
                    password = password_input.encode('utf-8')
                    hashed = bcrypt.hashpw(password, bcrypt.gensalt())

                    birthday_pattern = re.compile(r"\d{4}-\d{2}-\d{2}")
                    if not birthday_pattern.match(birthday):
                        flash("Date de naissance invalide")
                        return redirect(url_for('auth.register'))
                    
                    if data:
                        if data[9] != 0:
                            flash("Email déjà utilisé")
                            return redirect(url_for('auth.register'))
                        else:
                            cursor.execute("UPDATE users SET name=%s, birthday=%s, password=%s WHERE email=%s", (name, birthday, hashed, email))
                    else:
                        cursor.execute("INSERT INTO users (name, birthday, email, password) VALUES (%s, %s, %s, %s)", (name, birthday, email, hashed))
                    
                    secret_key = pyotp.random_base32()
                    totp = pyotp.TOTP(secret_key, interval=120)
                    session["2fa"]["id"] = None
                    session["2fa"]["email"] = email
                    session["2fa"]["code"] = totp.now()
                    session["2fa"]["action"] = "register"
                    session["2fa"]["secret_key"] = secret_key
                    session["2fa"]["totp"] = totp
                    session["2fa"]["expires"] = time.time() + 60
                    session["2fa"]["delay"] =  time.time() + 60
                    send_mail(email, "2FA code", f"Your 2FA code is: {session['2fa']['code']}")
                    return redirect(url_for('auth.sys_2fa'))
                else:
                    return redirect(url_for('auth.sys_2fa'))
        except Exception as e:
            print(e)
            flash('Erreur de connexion')
            return redirect(url_for('auth.register'))
        finally:
            if cursor:
                cursor.close()
            close_connection(conn)

@auth_bp.route('/2fa')
def sys_2fa():
    """
    Renders the 2FA (Two-Factor Authentication) page if the user is not authenticated and has a valid email in the session.
    Otherwise, redirects to the login page.

    Returns:
        If the user is authenticated, redirects to the home page.
        If the user does not have a valid email in the session, redirects to the login page.
        If the user has already checked the 2FA, redirects to the login page.
        Otherwise, renders the 'auth/2fa.html' template.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if session["2fa"]["email"] == None:
        return redirect(url_for('auth.login'))
    return render_template('auth/2fa.html')

@auth_bp.route('/2fa_sendCodeAgain')
def sys_2fa_sendCodeAgain():
    """
    Sends a new 2FA code to the user's email address and updates the session data.

    Returns:
        - If the user is authenticated, redirects to the main index page.
        - If the user's email is not set in the session, redirects to the login page.
        - If the 2FA check has already been completed, redirects to the login page.
        - If the delay time has not passed, flashes a message indicating the remaining time and redirects to the 2FA page.
        - Otherwise, generates a new 2FA code, updates the session data, sends the code to the user's email, flashes a success message, and redirects to the 2FA page.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if session["2fa"]["email"] == None:
        return redirect(url_for('auth.login'))
    if time.time() > session["2fa"]["delay"]:
        secret_key = session["2fa"]["secret_key"]
        totp = pyotp.TOTP(secret_key, interval=120)
        session["2fa"]["code"] = totp.now()
        session["2fa"]["totp"] = totp
        session["2fa"]["trials"] = 0
        session["2fa"]["expires"] = time.time() + 300
        session["2fa"]["delay"] =  time.time() + 60

        send_mail(session["2fa"]["email"], "2FA code", f"Your 2FA code is: {session['2fa']['code']}")
        flash("Nouveau code envoyé")
        return redirect(url_for('auth.sys_2fa'))
    else:
        flash("Vous devez attendre " + str(int(session["2fa"]["delay"] - time.time())) + " secondes avant de pouvoir envoyer un nouveau code")
        return redirect(url_for('auth.sys_2fa'))


@auth_bp.route('/2fa', methods=['POST'])
def sys_2fa_post():
    """
    Handle the POST request for the two-factor authentication (2FA) page.

    This function checks the user's authentication status and the 2FA session data to determine the appropriate action.
    If the user is already authenticated, they are redirected to the main index page.
    If the 2FA session does not have an email set, the user is redirected to the login page.
    If the 2FA session has been checked and the action is "login", the user is logged in and redirected to the main index page.
    If the 2FA session has been checked and the action is "register", the user is redirected to the register page with the email and a placeholder password.
    If the provided code is incorrect, the user is redirected back to the 2FA page with a flash message.
    If the provided code has expired, the user is redirected back to the 2FA page with a flash message.
    If there have been too many login attempts and the delay period has not passed, the user is redirected back to the 2FA page with a flash message indicating the remaining time before they can retry.
    If the provided code is correct and the action is "login", the user is logged in and redirected to the main index page.
    If the provided code is correct and the action is "register", the user is redirected to the register page with the email and a placeholder password.
    If none of the above conditions are met, the user is redirected back to the 2FA page with a flash message indicating an incorrect code.

    Returns:
        A redirect response based on the authentication and 2FA session data.
    """
    def _login(user_id):
        """
        Logs in the user with the given user_id.

        Parameters:
        user_id (int): The ID of the user to log in.

        Returns:
        redirect: A redirect response to the main index page.
        """
        user = User(user_id)
        login_user(user)
        session.pop("login_tries")
        session.pop("2fa")
        return redirect(url_for('main.index'))
    
    def _register(email):
        conn = None 
        cursor = None
        try:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET activated=TRUE WHERE email=%s", (email,))
            cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
            data = cursor.fetchone()
            user = User(data[0])
            login_user(user)

            session.pop("login_tries")
            session.pop("2fa")
            return redirect(url_for('main.index'))
        except Exception as e:
            print(e)
            flash('Une erreur est survenue lors de l\'activation de votre compte')
            return redirect(url_for('auth.register'))
        finally:
            if cursor:
                cursor.close()
            close_connection(conn)
    
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if session["2fa"]["email"] == None:
        return redirect(url_for('auth.login'))
    code = request.form.get('code')
    if not code:
        flash("Code incorrect")
        return redirect(url_for('auth.sys_2fa'))
    if time.time() > session["2fa"]["expires"]:
        flash("Code expiré")
        return redirect(url_for('auth.sys_2fa'))
    if session["2fa"]["trials"] >= 3 and session["2fa"]["delay"] > time.time():
        flash("Trop de tentatives de connexion, veuillez réessayer dans " + str(int(session["2fa"]["delay"] - time.time())) + " secondes")
        return redirect(url_for('auth.sys_2fa'))
    elif session["2fa"]["totp"].verify(code):
        if session["2fa"]["action"] == "login":
            return _login(session["2fa"]["id"])
        elif session["2fa"]["action"] == "register":
            return _register(session["2fa"]["email"])
    else:
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
    logout_user()
    return redirect(url_for('auth.login'))
