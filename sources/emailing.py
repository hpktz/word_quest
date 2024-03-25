""" 
This module is used to handle the emailing service.
Each day, at 6:00 PM, Google Cloud Scheduler triggers a POST request to the /api/automatisations/reminder route.

Imports:
    - smtplib: SMTP protocol client.
    - flask: For handling HTTP requests.
    - flask_wtf.csrf: CSRF protection for the application.
    - email.mime.text: MIMEText class for creating email messages.
    - email.mime.multipart: MIMEMultipart class for creating email messages.
    - email.mime.image: MIMEImage class for creating email messages.
    - os: Provides a way of using operating system dependent functionality.
    - random: Implements pseudo-random number generators for various distributions.
    - logging: Provides a flexible event logging system for applications.
    - functools: Provides tools for working with functions and other callable objects.
    - jwt: JSON Web Token implementation for Python.
    - root: Custom module for handling database connections. 

Functions:
    - token_required: Decorator function to check if the request has a valid token.
    - send_mail: Send an email to the recipient.
    - get_user_data: Get the user's data from the database.
"""
import smtplib
from flask import Blueprint, render_template, redirect, url_for, jsonify, request, session, abort
from flask_wtf.csrf import CSRFProtect
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os
from root import *
import random
import logging
from functools import wraps
import jwt

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        """
        Decorator function to check if the request has a valid token.

        Returns:
            dict: The response object.
                - code (int): The status code of the response.
                    -> 401: Unauthorized.
                - message (string): The message of the response.
            function: The decorated function.
        """
        token = None
        # Check if the token is in the request headers
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token'] 
        if not token:
            return jsonify({"code": 401, "message": "Unauthorized"}), 401
        # Check if the token is valid
        if token != os.environ.get('EMAILING_SERVICE_TOKEN'):
            return jsonify({"code": 401, "message": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

emailing_bp = Blueprint('emailing', __name__)
""" 
The emailing_bp Blueprint object for handling the emailing service.

Routes: 
    - /api/automatisations/reminder: Send a reminder email to the users.
    
Attributes:
    - emailing_bp: Blueprint object for handling the emailing service.
"""

def send_mail(to, subject, body, main_img, notif_remind, notif_stats):
    """
    Send an email.

    Args:
        to (string): The recipient's email address.
        subject (string): The subject of the email.
        body (string): The body of the email.
        main_img (string): The path to the main image of the email.
        notif_remind (bool): True if the reminder notification is enabled, False otherwise.
        notif_stats (bool): True if the statistics notification is enabled, False otherwise.

    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    
    # Create the email message
    mess = MIMEMultipart()
    mess['From'] = 'Word Quest <no-reply@word-quest.com>'
    mess['To'] = to
    mess['Subject'] = subject

    # Attach the body to the message
    mess.attach(MIMEText(body, 'html'))
    
    with open(str(os.getenv("DIRECTORY_PATH")) + 'static/imgs/app-main-logo.png', 'rb') as fp:
        img = MIMEImage(fp.read())
        img.add_header('Content-ID', '<{}>'.format('app-main-logo'))
        mess.attach(img)
        
    with open(main_img, 'rb') as fp:
        img = MIMEImage(fp.read())
        img.add_header('Content-ID', '<{}>'.format('main-picture'))
        mess.attach(img)
        
    if notif_remind:
        with open(str(os.getenv("DIRECTORY_PATH")) + 'static/imgs/opened-chest.png', 'rb') as fp:
            img = MIMEImage(fp.read())
            img.add_header('Content-ID', '<{}>'.format('chest-illustration'))
            mess.attach(img)
    
    if notif_stats:
        with open(str(os.getenv("DIRECTORY_PATH")) + 'static/imgs/3d-three-yelow-lightnings.png', 'rb') as fp:
            img = MIMEImage(fp.read())
            img.add_header('Content-ID', '<{}>'.format('lightnings-illustration'))
            mess.attach(img)
            
        with open(str(os.getenv("DIRECTORY_PATH")) + 'static/imgs/3d-red-clock.png', 'rb') as fp:
            img = MIMEImage(fp.read())
            img.add_header('Content-ID', '<{}>'.format('red-clock-illustration'))
            mess.attach(img)

    server = None
    try:
        # Send the email
        server = smtplib.SMTP('smtp.ionos.fr', 587)
        server.starttls()
        server.login('no-reply@word-quest.com', os.environ.get('EMAILING_SERVICE_PASSWORD'))
        server.sendmail(mess['From'], mess['To'], mess.as_string())
        return True    
    except Exception as e:
        logging.error(e)
        return False
    finally:
        if server:
            server.quit()


def get_user_data(user_id):
    """
    Get the user's data from the database.
    
    Args:
        user_id (int): The ID of the user.
        
    Returns:
        dict: The user's data.
            - notif_remind (bool): True if the reminder notification is enabled, False otherwise.
            - notif_stats (bool): True if the statistics notification is enabled, False otherwise.
            - got_rewards (bool): True if the user got rewards today, False otherwise.
            - games (int): The number of games played today.
            - time (int): The time spent today.
            - xp (int): The experience points earned today.
            - user_rank (int): The user's rank.
            - main_picture (string): The path to the main image of the email.
            - main_title (string): The title of the email.
            - final_sentence (string): The final sentence of the email.
        dict: An empty dictionary if an error occurred.
    """
    targets = {"games": 0, "xp": 0,"time": 0}
    
    conn = None
    cursor = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        # Get the user's data
        cursor.execute("SELECT * FROM lists WHERE user_id = %s AND (notif_remind = 1 OR notif_stats = 1)", (user_id,))
        lists = cursor.fetchall()
        if lists:
            # Check if the user has the reminder and statistics notifications enabled
            notif_remind = False if not any(lst[12] == 1 for lst in lists) else True
            notif_stats = False if not any(lst[13] == 1 for lst in lists) else True
            
            # Check if the user got rewards today
            cursor.execute("SELECT * FROM rewards WHERE user_id = %s AND DATE(created_at) = CURRENT_DATE()", (user_id,))
            got_rewards = True if cursor.fetchall() else False
            
            # Check the user's statistics today
            cursor.execute("SELECT COALESCE(COUNT(*), 0), COALESCE(SUM(time), 0), COALESCE(SUM(xp), 0) FROM lessons_log WHERE user_id = %s AND DATE(created_at) = CURRENT_DATE()", (user_id,))
            lessons_log = cursor.fetchone()
            if lessons_log:
                games = lessons_log[0]
                time = lessons_log[1]
                xp = lessons_log[2]
            else:
                games = 0
                time = 0
                xp = 0
            
            # Get the user's rank
            cursor.execute("SELECT u.id as user_id, u.name as username, SUM(ll.xp) as total_xp, \
            RANK() OVER (ORDER BY SUM(ll.xp) DESC) as user_rank FROM users u JOIN lessons_log ll ON u.id = ll.user_id \
            GROUP BY u.id, u.name ORDER BY total_xp DESC;")
            ranking = cursor.fetchall()
            user_rank = 0
            
            for item, rank in enumerate(ranking):
                if int(rank[0]) == int(user_id):
                    user_rank = int(rank[3])
                    break   
            
            # Get the main picture and title of the email
            main_pictures = [
                "static/imgs/emails/3d-business-female-student-with-notebooks.png",
                "static/imgs/emails/3d-business-joyful-man-with-phone-waving-his-hand.png",
                "static/imgs/emails/3d-business-joyful-woman-pointing-diagonally.png",
                "static/imgs/emails/3d-business-joyful-woman-raising-her-fist-up.png",
                "static/imgs/emails/3d-business-young-man-watching-something-in-vr-glasses.png",
                "static/imgs/emails/3d-business-young-man-with-a-phone-in-his-hands-taking-a-selfie.png",
                "static/imgs/emails/3d-business-young-woman-with-bag-pointing-up.png",
                "static/imgs/emails/3d-casual-life-happy-thankful-man-holding-folded-hands-near-heart.png",
            ]
            main_picture = str(os.getenv("DIRECTORY_PATH")) + random.choice(main_pictures)
            main_titles = [
                "Bonne soirée !",
                "Bonsoir !",
                "Salut !",
                "Hello !",
                "Hi !",
                "Good evening !"
            ]
            main_title = random.choice(main_titles)
            if xp > 50:
                final_sentence = "Tu as déjà gagné plus de 50 points d'expérience aujourd'hui ! Impressionnant !"
            elif xp > 25:
                final_sentence = "Tu as déjà gagné plus de 25 points d'expérience aujourd'hui ! L'excellence est à portée de main !"
            elif xp > 0:
                final_sentence = "Tu as déjà gagné quelques points d'expérience aujourd'hui !  Tu es sur la bonne voie !"
            else:
                final_sentence = "Tu n'as pas encore gagné de points d'expérience aujourd'hui. N'oublie pas de jouer !"
            
            # Return the user's data
            if notif_remind and not got_rewards or notif_stats:
                return {
                    "notif_remind": notif_remind,
                    "notif_stats": notif_stats,
                    "got_rewards": got_rewards,
                    "games": games,
                    "time": time,
                    "xp": xp,
                    "user_rank": user_rank,
                    "main_picture": main_picture,
                    "main_title": main_title,
                    "final_sentence": final_sentence
                }
            else:
                return {}
        else:
            return {}
        
    except Exception as e:
        logging.error(e)
        return {}
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@emailing_bp.route('/api/automatisations/reminder', methods=["POST"])
@token_required
def reminder_auto():
    """
    Send a reminder email to the users.
    
    Returns:
        dict: The response object.
            - code (int): The status code of the response.
                -> 200: OK.
                -> 500: Internal Server Error.
            - message (string): The message of the response.
    """
    conn = None
    cursor = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        # Get the list of users
        cursor.execute("SELECT id, email FROM users")
        users_id = cursor.fetchall()
        # For each user, get the user's data and check the availability of the reminder and statistics notifications
        for user_id in users_id:
            user_data = get_user_data(user_id[0])
            # If the user's data is available, send the reminder email
            if user_data:
                html = render_template(
                    "emails/remind-email-and-stats.html",
                    notif_remind=user_data["notif_remind"],
                    notif_stats=user_data["notif_stats"],
                    got_rewards=user_data["got_rewards"],
                    games=user_data["games"],
                    time=user_data["time"],
                    xp=user_data["xp"],
                    user_rank=user_data["user_rank"],
                    main_picture=user_data["main_picture"],
                    main_title=user_data["main_title"],
                    final_sentence=user_data["final_sentence"]
                )
                notif_remind = user_data["notif_remind"] and not user_data["got_rewards"]
                send_mail(user_id[1], "Rappel quotidien", html, user_data["main_picture"], notif_remind, user_data["notif_stats"])
        return jsonify({"code": 200, "message": "OK"})
    except Exception as e:
        logging.error(e)
        return jsonify({"code": 500, "message": "Internal Server Error"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()