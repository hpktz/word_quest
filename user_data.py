from flask import Blueprint, render_template, redirect, url_for, jsonify, request, session, abort
from flask_login import login_user, login_required, logout_user, current_user
from root import *
import random as random
import logging as logging
from datetime import datetime, timedelta
import locale
import json
import bcrypt
import pyotp
import time

from sendmails import send_mail

user_data_bp = Blueprint('user_data', __name__)

@user_data_bp.route('/dashboard/profile/user')
def user_profile_redirect():
    return redirect(url_for('user_data.user_profile', id = 0))


@user_data_bp.route('/dashboard/profile/user/<int:id>')
@login_required
def user_profile(id):
    if id == 0:
        is_current_user = True
        user_id = current_user.id
    elif int(id) == int(current_user.id):
        is_current_user = True
        user_id = id
    else:
        is_current_user = False
        user_id = id
        
    conn = None
    cursor = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        if not result:
            abort(404)
            
        is_public = False if result[7] == 0 else True
        picture = result[8]
        name = result[1]
        date = result[12].date()
        date = date.strftime("%d %B %Y")
            
        subscriptions = []
        cursor.execute("SELECT users.id, users.name, users.picture, \
                SUM(CASE WHEN user_statements.transaction_type = 'xp' THEN user_statements.transaction ELSE 0 END) \
                AS sum_xp FROM subscriptions JOIN users ON users.id = subscriptions.subscribed_to \
                JOIN user_statements ON users.id = user_statements.user_id WHERE \
                subscriptions.user_id = %s;", (user_id,))
        result = cursor.fetchall()
        
        for row in result:
            if row[0] is None:
                continue
            subscriptions.append(row)
        
        subscribers = []
        cursor.execute("SELECT users.id, users.name, users.picture, \
                SUM(CASE WHEN user_statements.transaction_type = 'xp' THEN user_statements.transaction ELSE 0 END) \
                AS sum_xp, false AS is_subscribed, subscriptions.created_at  FROM subscriptions JOIN users ON users.id = subscriptions.user_id \
                JOIN user_statements ON users.id = user_statements.user_id WHERE \
                subscriptions.subscribed_to = %s;", (user_id,))
        result = cursor.fetchall()
        for row in result:
            if row[0] is None:
                continue
            row = list(row)
            if is_current_user:
                is_subscribed = False
                for sub in subscriptions:
                    if sub[0] == row[0]:
                        is_subscribed = True
                        break
                row[5] = is_subscribed
            subscribers.append(row)
            
        is_subscribed = False
        if not is_public and not is_current_user:
            for sub in subscriptions:
                print(sub)
                if int(sub[0]) == int(current_user.id):
                    is_subscribed = True
                    break
            
        are_you_subscribed = False
        subscribed_date = None
        for sub in subscribers:
            if int(sub[0]) == int(current_user.id):
                are_you_subscribed = True
                subscribed_date = sub[5].date().strftime("%d %B %Y")
                break
            
        user_infos = {}
        if is_public or is_current_user or is_subscribed:
            user_infos["xp"] = 0
            user_infos["gems"] = 0
            cursor.execute("SELECT SUM(CASE WHEN transaction_type = 'xp' THEN transaction ELSE 0 END) AS sum_xp, \
                    SUM(CASE WHEN transaction_type = 'gems' THEN transaction ELSE 0 END) AS sum_gems FROM user_statements \
                    WHERE user_id = %s;", (user_id,))
            result = cursor.fetchone()
            if result:
                if result[0] is not None:   
                    user_infos["xp"] = result[0]
                    user_infos["gems"] = result[1]
                
            user_infos["rank"] = 0
            cursor.execute("SELECT u.id as user_id, u.name as username, SUM(ll.xp) as total_xp, \
                RANK() OVER (ORDER BY SUM(ll.xp) DESC) as user_rank FROM users u JOIN lessons_log ll ON u.id = ll.user_id \
                GROUP BY u.id, u.name ORDER BY total_xp DESC;")
            ranking = cursor.fetchall()
            
            user_infos["rank"] = next((rank[3] for rank in ranking if rank[0] == user_id), 0)
            
            user_infos["lists"] = []
            cursor.execute("SELECT id, initial_id, title, public, created_at FROM lists WHERE user_id = %s;", (user_id,))
            results = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            for row in results:
                if row[3] == 0 and not is_current_user and not is_subscribed:
                    continue
                
                result = dict(zip(columns, row))
                
                result["created_at"] = result["created_at"].date()
                # calculer le nombre de mois, ou de semaines, ou de jours depuis la création de la liste
                gap = datetime.now().date() - result["created_at"]
                if gap.days > 30:
                    result["created_at"] = str(int(gap.days/30)) + " mois" + ("s" if int(gap.days/30) > 1 else "")
                elif gap.days > 7:
                    result["created_at"] = str(int(gap.days/7)) + " semaine" + ("s" if int(gap.days/7) > 1 else "")
                else:
                    result["created_at"] = str(gap.days) + " jour" + ("s" if gap.days > 1 else "")

                result["words"] = []
                result["lessons"] = []
                
                is_yours = False
                if result["initial_id"] is not None:
                    is_yours = any(list["id"] == result["initial_id"] for list in current_user.lists)
                
                result["is_yours"] = is_yours

                cursor.execute('SELECT id, word, word_type, examples, trans_word, trans_examples FROM list_content WHERE list_id = %s', (result["id"],))
                words = cursor.fetchall()

                for word in words:
                    result["words"].append({
                        "word": word[1],
                        "type": word[2],
                        "examples": json.loads(word[3]),
                        "trans_word": word[4],
                        "trans_examples": json.loads(word[5])
                    })
                user_infos["lists"].append(result)
        
    except mysql.connector.Error as e:
        print(e)
        abort(500)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    return render_template('dashboard/profile.html', 
                           id = user_id,
                           name = name,
                           date = date,
                           picture = picture,
                           are_you_subscribed = are_you_subscribed,
                           subscribed_date = subscribed_date,
                           subscriptions = subscriptions, 
                           subscribers = subscribers, 
                           is_current_user = is_current_user,
                           user_infos = user_infos)
    
    
@user_data_bp.route('/dashboard/profile/user/search/<string:name>')
@login_required
def search_user(name):
    conn = None
    cursor = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT users.id, users.name, users.picture, \
                SUM(CASE WHEN user_statements.transaction_type = 'xp' THEN user_statements.transaction ELSE 0 END) \
                AS sum_xp FROM users \
                JOIN user_statements ON users.id = user_statements.user_id WHERE \
                users.name =  %s;", (name,))
        result = cursor.fetchall()
        if not result or result[0][0] is None:
            return jsonify({
                "code": 404,
                "message": "Aucun utilisateur trouvé.",
                "result": []
            })
        else:
            return jsonify({
                "code": 200,
                "message": "Utilisateur trouvé.",
                "result": result
            })
        
    except mysql.connector.Error as e:
        print(e)
        abort(500)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
            
@user_data_bp.route('/dashboard/profile/user/subscribe/<int:id>')
@login_required
def subscribe(id):
    conn = None
    cursor = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM subscriptions WHERE user_id = %s AND subscribed_to = %s;", (current_user.id, id))
        result = cursor.fetchone()
        if result:
            return jsonify({
                "code": 400,
                "message": "Vous êtes déjà abonné à cet utilisateur."
            })
        else:
            cursor.execute("INSERT INTO subscriptions (user_id, subscribed_to) VALUES (%s, %s);", (current_user.id, id))
            conn.commit()
            return jsonify({
                "code": 200,
                "message": "Vous êtes maintenant abonné à cet utilisateur."
            })
        
    except mysql.connector.Error as e:
        print(e)
        abort(500)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
@user_data_bp.route('/dashboard/profile/user/unsubscribe/<int:id>')
@login_required
def unsubscribe(id):
    conn = None
    cursor = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM subscriptions WHERE user_id = %s AND subscribed_to = %s;", (current_user.id, id))
        result = cursor.fetchone()
        if not result:
            return jsonify({
                "code": 400,
                "message": "Vous n'êtes pas abonné à cet utilisateur."
            })
        else:
            cursor.execute("DELETE FROM subscriptions WHERE user_id = %s AND subscribed_to = %s;", (current_user.id, id))
            conn.commit()
            return jsonify({
                "code": 200,
                "message": "Vous n'êtes plus abonné à cet utilisateur."
            })
        
    except mysql.connector.Error as e:
        print(e)
        abort(500)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
@user_data_bp.route('/dashboard/settings')
def settings():
    return render_template('dashboard/settings.html')


@user_data_bp.route('/dashboard/settings/change-password', methods = ['POST'])
@login_required
def change_password():
    old_password = request.json.get('old_password')
    new_password = request.json.get('new_password')
    mfa = request.json.get('mfa')

    conn = None
    cursor = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE id = %s;", (current_user.id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({
                "code": 404,
                "message": "Utilisateur introuvable."
            })
        if not bcrypt.checkpw(old_password.encode('utf-8'), result[0].encode('utf-8')):
            return jsonify({
                "code": 400,
                "message": "Ancien mot de passe incorrect."
            })
        
        mfa = bool(mfa)
        new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        
        cursor.execute("UPDATE users SET password = %s, 2fa = %s WHERE id = %s;", (new_password, mfa, current_user.id))
        conn.commit()
        return jsonify({
            "code": 200,
            "message": "Mot de passe modifié avec succès."
        })
        
    except mysql.connector.Error as e:
        print(e)
        abort(500)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    
@user_data_bp.route('/dashboard/settings/change-user-infos', methods = ['POST'])
@login_required
def change_user_infos():
    name = request.json.get('username')
    email = request.json.get('email')
    picture = request.json.get('profilePicture')

    conn = None
    cursor = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        picture = int(picture)
        if not picture in range(1,12):
            return jsonify({
                "code": 400,
                "message": "Image de profil invalide."
            })
        picture = "picture-" + str(picture)
        if email == current_user.email:
            
            cursor.execute("UPDATE users SET name = %s, picture = %s WHERE id = %s;", (name, picture, current_user.id))
            return jsonify({
                "code": 200,
                "message": "Informations modifiées avec succès."
            })
        else:
            cursor.execute("SELECT * FROM users WHERE email = %s;", (email,))
            result = cursor.fetchone()
            if result:
                return jsonify({
                    "code": 400,
                    "message": "Adresse mail déjà utilisée."
                })
            else:
                if "2fa" not in session or session["2fa"]["expires"] < time.time():
                    secret_key = pyotp.random_base32()
                    totp = pyotp.TOTP(secret_key)
                    
                    session["2fa"] = {
                        "username": name,
                        "email": email,
                        "picture": picture,
                        "secret_key": secret_key,
                        "expires": time.time() + 60
                    }
                    send_mail(email, "Vérification de votre adresse mail", "Votre code de vérification est : " + totp.now())
                    return jsonify({
                        "code": 201,
                        "message": "Un code de vérification a été envoyé à votre adresse mail."
                    })         
                else:
                    return jsonify({
                        "code": 400,
                        "message": "Un code a déjà été envoyé."
                    })
            
    except mysql.connector.Error as e:
        print(e)
        abort(500)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()    
            
@user_data_bp.route('/dashboard/settings/verify-email/<string:code>')
@login_required
def verify_email(code):
    if "2fa" not in session or session["2fa"]["expires"] < time.time():
        return jsonify({
            "code": 400,
            "message": "Code expiré."
        })
    totp = pyotp.TOTP(session["2fa"]["secret_key"])
    if not totp.verify(code, valid_window=1):
        return jsonify({
            "code": 400,
            "message": "Code invalide."
        })
    
    conn = None
    cursor = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET name = %s, email = %s, picture = %s WHERE id = %s;", (session["2fa"]["username"], session["2fa"]["email"], session["2fa"]["picture"], current_user.id))
        del session["2fa"]
        return jsonify({
            "code": 200,
            "message": "Adresse mail modifiée avec succès."
        })
        
    except mysql.connector.Error as e:
        print(e)
        abort(500)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()    
            
@user_data_bp.route('/dashboard/settings/change-visibility/<int:visibility>')
@login_required
def change_visibility(visibility):
    conn = None
    cursor = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET public = %s WHERE id = %s;", (visibility, current_user.id))
        conn.commit()
        return jsonify({
            "code": 200,
            "message": "Visibilité modifiée avec succès."
        })
        
    except mysql.connector.Error as e:
        print(e)
        abort(500)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()