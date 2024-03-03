""" 
This module contains the send_mail function for the application.

Imports:
    - smtplib: SMTP protocol client.
    - MIMEText: Class for generating plain text email messages.
    - MIMEMultipart: Class for generating multipart email messages.
    - MIMEImage: Class for generating image email messages.
    - os: Miscellaneous operating system interfaces.

Functions:
    - send_mail: Send an email.
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
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({"code": 401, "message": "Unauthorized"}), 401
        if token != os.environ.get('EMAILING_SERVICE_TOKEN'):
            return jsonify({"code": 401, "message": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

emailing_bp = Blueprint('emailing', __name__)

def send_mail(to, subject, body, main_img, notif_remind, notif_stats):
    """
    Send an email.

    Args:
        to (string): The recipient's email address.
        subject (string): The subject of the email.
        body (string): The body of the email.

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
    
    with open('static/imgs/app-main-logo.png', 'rb') as fp:
        img = MIMEImage(fp.read())
        img.add_header('Content-ID', '<{}>'.format('app-main-logo'))
        mess.attach(img)
        
    with open(main_img, 'rb') as fp:
        img = MIMEImage(fp.read())
        img.add_header('Content-ID', '<{}>'.format('main-picture'))
        mess.attach(img)
        
    if notif_remind:
        with open('static/imgs/opened-chest.png', 'rb') as fp:
            img = MIMEImage(fp.read())
            img.add_header('Content-ID', '<{}>'.format('chest-illustration'))
            mess.attach(img)
    
    if notif_stats:
        with open('static/imgs/3d-three-yelow-lightnings.png', 'rb') as fp:
            img = MIMEImage(fp.read())
            img.add_header('Content-ID', '<{}>'.format('lightnings-illustration'))
            mess.attach(img)
            
        with open('static/imgs/3d-red-clock.png', 'rb') as fp:
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
    targets = {"games": 0, "xp": 0,"time": 0}
    
    conn = None
    cursor = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM lists WHERE user_id = %s AND (notif_remind = 1 OR notif_stats = 1)", (user_id,))
        lists = cursor.fetchall()
        if lists:
            notif_remind = False if not any(lst[12] == 1 for lst in lists) else True
            notif_stats = False if not any(lst[13] == 1 for lst in lists) else True
            
            cursor.execute("SELECT * FROM rewards WHERE user_id = %s AND DATE(created_at) = CURRENT_DATE()", (user_id,))
            got_rewards = True if cursor.fetchall() else False
            
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
                
            cursor.execute("SELECT u.id as user_id, u.name as username, SUM(ll.xp) as total_xp, \
            RANK() OVER (ORDER BY SUM(ll.xp) DESC) as user_rank FROM users u JOIN lessons_log ll ON u.id = ll.user_id \
            GROUP BY u.id, u.name ORDER BY total_xp DESC;")
            ranking = cursor.fetchall()
            user_rank = 0
            
            for item, rank in enumerate(ranking):
                if int(rank[0]) == int(user_id):
                    user_rank = int(rank[3])
                    break   
            
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
            main_picture = random.choice(main_pictures)
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
    conn = None
    cursor = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, email FROM users")
        users_id = cursor.fetchall()
        for user_id in users_id:
            user_data = get_user_data(user_id[0])
            print(user_data)
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