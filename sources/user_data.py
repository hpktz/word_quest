"""
This module contains the routes for the user's profile and settings.

Imports:
    - flask: For handling the requests and responses.
    - flask_login: For handling the user's session.
    - root: For the connection to the database.
    - random: For generating random numbers.
    - logging: For logging errors.
    - datetime: For handling dates.
    - locale: For handling the date format.
    - json: For handling json data.
    - bcrypt: For hashing the password.
    - pyotp: For handling the two-factor authentication.
    - time: For handling the time.
    - send_mail: For sending emails.
    - logging: For logging errors.
    
Blueprints:
    - user_data_bp: The blueprint for the user's profile and settings.

"""

from flask import Blueprint, render_template, redirect, url_for, jsonify, request, session, abort
from flask_login import login_user, login_required, logout_user, current_user
from root import *
import random as random
import logging as logging
from datetime import datetime, timedelta
import json
import bcrypt
import pyotp
import time
import logging

from sendmails import send_mail

user_data_bp = Blueprint('user_data', __name__)
"""
The blueprint for the user's profile and settings.

Attributes:
    - user_data_bp: The blueprint for the user's profile and settings.
    
Routes:
    - /dashboard/profile/user: To display the user's profile.
    - /dashboard/profile/user/<int:id>: To display other user's profile.
    - /dashboard/profile/user/search/<string:name>: To search for a user.
    - /dashboard/profile/user/subscribe/<int:id>: To subscribe to a user.
    - /dashboard/profile/user/unsubscribe/<int:id>: To unsubscribe from a user.
    - /dashboard/settings: To display the settings page.
    - /dashboard/settings/change-password: To change the user's password.
    - /dashboard/settings/change-user-infos: To change the user's informations.
    - /dashboard/settings/verify-email/<string:code>: To verify the user's email.
    - /dashboard/settings/change-visibility/<int:visibility>: To change the user's visibility.
    - /dashboard/settings/delete-account: To delete the user's account.
"""

@user_data_bp.route('/dashboard/profile/user')
def user_profile_redirect():
    """
    Display the user's profile.

    Returns:
        flask.redirect: Redirect to the user's profile.
    """
    return redirect(url_for('user_data.user_profile', id = 0))


@user_data_bp.route('/dashboard/profile/user/<int:id>')
@login_required
def user_profile(id):
    """
    Display the user's profile.
    
    This function retrieves the user's informations from the database and displays them on the user's profile page.
    If the user's profile is public, the user's informations are displayed.
    If the user's profile is private, the user's informations are displayed if the current user is on  the user's subscriptions list.
    If the user's profile is private and the current user is not on the user's subscriptions list, the user's informations are not displayed.

    Args:
        id (int): The user's id.

    Returns:
        flask.render_template: The user's profile page.
    """
    # If the user's id is 0, the current user's profile is displayed.
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
        
        # Retrieve the user's informations from the database.
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        if not result:
            abort(404) # If the user was not found, return a 404 error.
            
        is_public = False if result[7] == 0 else True
        picture = result[8]
        name = result[1]
        date = result[13].date()
            
        # Retrieve the user's subscriptions and subscribers from the database.
        subscriptions = []
        cursor.execute("SELECT users.id, users.name, users.picture, \
                SUM(CASE WHEN user_statements.transaction_type = 'xp' THEN user_statements.transaction ELSE 0 END) \
                AS sum_xp FROM subscriptions JOIN users ON users.id = subscriptions.subscribed_to \
                JOIN user_statements ON users.id = user_statements.user_id WHERE \
                subscriptions.user_id = %s GROUP BY users.id, users.name, users.picture;", (user_id,))
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
                subscriptions.subscribed_to = %s GROUP BY users.id, users.name, users.picture;", (user_id,))
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
            
        # Check if the user is subscribed to the current user.
        is_subscribed = False
        if not is_public and not is_current_user:
            for sub in subscriptions:
                if int(sub[0]) == int(current_user.id):
                    is_subscribed = True
                    break
            
        # Check if the current user is subscribed to the user.
        are_you_subscribed = False
        subscribed_date = None
        for sub in subscribers:
            if int(sub[0]) == int(current_user.id):
                are_you_subscribed = True
                subscribed_date = sub[5] 
                # Transform into datetime
                subscribed_date = convert_date(sub[5].date())
                break
            
        user_infos = {}
        # Retrieve the user's xp, gems and rank from the database.
        # Only if the profile is accessible.
        if is_public or is_current_user or is_subscribed:
            # Retrieve the user's xp and gems from the database.
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
                
            # Retrieve the user's rank from the database.
            user_infos["rank"] = 0
            cursor.execute("SELECT u.id as user_id, u.name as username, SUM(ll.xp) as total_xp, \
                RANK() OVER (ORDER BY SUM(ll.xp) DESC) as user_rank FROM users u JOIN lessons_log ll ON u.id = ll.user_id \
                GROUP BY u.id, u.name ORDER BY total_xp DESC;")
            ranking = cursor.fetchall()
            
            user_infos["rank"] = next((rank[3] for rank in ranking if int(rank[0]) == int(user_id)), 0)
            # Retrieve the user's lists from the database.
            user_infos["lists"] = []
            cursor.execute("SELECT id, initial_id, title, public, created_at FROM lists WHERE user_id = %s;", (user_id,))
            results = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            for row in results:
                if row[3] == 0 and not is_current_user and not is_subscribed:
                    continue
                
                result = dict(zip(columns, row))

                # Format the date of creation.
                result["created_at"] = result["created_at"].date()
                gap = datetime.now().date() - result["created_at"]
                if gap.days > 30:
                    result["created_at"] = str(int(gap.days/30)) + " mois" + ("s" if int(gap.days/30) > 1 else "")
                elif gap.days > 7:
                    result["created_at"] = str(int(gap.days/7)) + " semaine" + ("s" if int(gap.days/7) > 1 else "")
                else:
                    result["created_at"] = str(gap.days) + " jour" + ("s" if gap.days > 1 else "")

                # Retrieve the words and lessons of the list from the database.
                result["words"] = []
                result["lessons"] = []
                
                # Check if the list is from the current user.
                is_yours = False
                if result["initial_id"] is not None:
                    is_yours = any(list["id"] == result["initial_id"] for list in current_user.get_lists())
                
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
        logging.error("Error while retrieving user's profile: " + str(e))
        abort(500)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    return render_template('dashboard/profile.html', 
                           id = user_id,
                           name = name,
                           date = convert_date(date),
                           picture = picture,
                           are_you_subscribed = are_you_subscribed,
                           subscribed_date = subscribed_date,
                           subscriptions = subscriptions, 
                           subscribers = subscribers, 
                           is_current_user = is_current_user,
                           is_public = is_public,
                           user_infos = user_infos)
    
    
@user_data_bp.route('/dashboard/profile/user/search/<string:name>')
@login_required
def search_user(name):
    """
    Search for a user.
    
    This function searches for a user in the database and returns the user's informations.

    Args:
        name (string): The user's name.

    Returns:
        dict: The user's informations.
            - code (int): The status code.
                -> 200: The user was found.
                -> 404: No user found.
            - message (string): The status message.
            - result (list): The user's informations.
    
    Raises:
        500: If there is an error while searching for the user in the database.
    """
    conn = None
    cursor = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        # Search for the user in the database.
        cursor.execute("SELECT users.id, users.name, users.picture, \
                SUM(CASE WHEN user_statements.transaction_type = 'xp' THEN user_statements.transaction ELSE 0 END) \
                AS sum_xp FROM users \
                JOIN user_statements ON users.id = user_statements.user_id WHERE \
                users.name LIKE  %s;", (name+ '%',))
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
        logging.error("Error while searching for user: " + str(e))
        abort(500)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
            
@user_data_bp.route('/dashboard/profile/user/subscribe/<int:id>')
@login_required
def subscribe(id):
    """
    Subscribe to a user.
    
    This function subscribes the current user to another user.
    
    Args:
        id (int): The user's id.
        
    Returns:
        dict: The status message.
            - code (int): The status code.
                -> 200: The user was subscribed.
                -> 400: The user is already subscribed.
            - message (string): The status message.
            
    Raises:
        500: If there is an error while subscribing to the user in the database.
    """
    conn = None
    cursor = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        # Check if the user is already subscribed.
        cursor.execute("SELECT * FROM subscriptions WHERE user_id = %s AND subscribed_to = %s;", (current_user.id, id))
        result = cursor.fetchone()
        if result:
            return jsonify({
                "code": 400,
                "message": "Vous êtes déjà abonné à cet utilisateur."
            })
        else:
            # Subscribe to the user.
            cursor.execute("INSERT INTO subscriptions (user_id, subscribed_to) VALUES (%s, %s);", (current_user.id, id))
            conn.commit()
            return jsonify({
                "code": 200,
                "message": "Vous êtes maintenant abonné à cet utilisateur."
            })
        
    except mysql.connector.Error as e:
        logging.error("Error while subscribing to user: " + str(e))
        abort(500)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
@user_data_bp.route('/dashboard/profile/user/unsubscribe/<int:id>')
@login_required
def unsubscribe(id):
    """
    Unsubscribe from a user.
    
    This function unsubscribes the current user from another user.

    Args:
        id (int): The user's id.
        
    Returns:
        dict: The status message.
            - code (int): The status code.
                -> 200: The user was unsubscribed.
                -> 400: The user is not subscribed.
            - message (string): The status message.
            
    Raises:
        500: If there is an error while unsubscribing from the user in the database.
    """
    conn = None
    cursor = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        # Check if the user is subscribed.
        cursor.execute("SELECT * FROM subscriptions WHERE user_id = %s AND subscribed_to = %s;", (current_user.id, id))
        result = cursor.fetchone()
        if not result:
            return jsonify({
                "code": 400,
                "message": "Vous n'êtes pas abonné à cet utilisateur."
            })
        else:
            # Unsubscribe from the user.
            cursor.execute("DELETE FROM subscriptions WHERE user_id = %s AND subscribed_to = %s;", (current_user.id, id))
            conn.commit()
            return jsonify({
                "code": 200,
                "message": "Vous n'êtes plus abonné à cet utilisateur."
            })
        
    except mysql.connector.Error as e:
        logging.error("Error while unsubscribing from user: " + str(e))
        abort(500)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
            
@user_data_bp.route('/dashboard/profile/list/<int:id>')
@login_required
def profile_list(id):
    conn = None
    cursor = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM lists WHERE id = %s;", (id,))
        result = cursor.fetchone()
        if not result:
            abort(404)
            
        name = result[7]
        desc = result[8]
        created_at = result[15]

        list_owner = result[2]
        cursor.execute("SELECT name FROM users WHERE id = %s;", (list_owner,))
        list_owner_name = cursor.fetchone()[0]
        is_public = False if result[4] == 0 else True
        is_yours = str(list_owner) == str(current_user.id)
        
        if not is_public and not is_yours:
            cursor.execute("SELECT * FROM subscriptions WHERE user_id = %s AND subscribed_to=%s;", (list_owner,current_user.id))
            result = cursor.fetchone()
            if not result:
                abort(404)
        
        cursor.execute("SELECT COUNT(*) FROM list_likes WHERE list_id = %s;", (id,))
        result = cursor.fetchone()
        likes = result[0]
        
        cursor.execute("SELECT id FROM lists WHERE initial_id = %s;", (id,))
        result = cursor.fetchall()
        copies = len(result)
        
        copies_id = [row[0] for row in result]
        copies_id.append(id)
        copies_id = ','.join(map(str, copies_id))
        print(copies_id)
        
        # Récupérer les xp gagnés par jour pour toutes les listes avec cet initial_id
        cursor.execute("SELECT SUM(xp) FROM lessons_log WHERE list_id IN ("+ copies_id +")",)
        result = cursor.fetchall()
        total_xp = result[0][0] if result[0][0] is not None else 0
        
        cursor.execute("SELECT * FROM list_content WHERE list_id = %s;", (id,))
        words = cursor.fetchall()
        words = [list(row) for row in words]
        for row in words:
            row[4] = json.loads(row[4])
            row[6] = json.loads(row[6])
            
        return render_template('dashboard/list-profile.html',
                               id = id,
                               name = name,
                               desc = desc,
                               list_owner = list_owner,
                               list_owner_name = list_owner_name,
                               created_at = convert_date(created_at),
                               likes = likes,
                               copies = copies,
                               total_xp = total_xp,
                               words = words,
                               is_public = is_public,
                               is_yours = is_yours)

                       
    except Exception as e:
        logging.error("Error while retrieving list: " + str(e))
        abort(500)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
                
@user_data_bp.route('/dashboard/settings')
def settings():
    """
    Display the settings page.
    
    Returns:
        flask.render_template: The settings page.
    """
    return render_template('dashboard/settings.html')


@user_data_bp.route('/dashboard/settings/change-password', methods = ['POST'])
@login_required
def change_password():
    """ 
    Change the user's password.
    
    This function changes the user's password in the database.
    
    Args:
        old_password (string): The user's old password.
        new_password (string): The user's new password.
        mfa (string): The user's two-factor authentication.
    
    Returns:
        dict: The status message.
            - code (int): The status code.
                -> 200: The password was changed.
                -> 400: The old password is incorrect.
                -> 404: The user was not found.
            - message (string): The status message.
            
    Raises:
        500: If there is an error while updating the password in the database.
    """
    old_password = request.json.get('old_password')
    new_password = request.json.get('new_password')
    mfa = request.json.get('mfa')

    conn = None
    cursor = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        # Retrieve the user's password from the database.
        cursor.execute("SELECT password FROM users WHERE id = %s;", (current_user.id,))
        result = cursor.fetchone()
        
        # Check if the user wanted to change the password or/and the two-factor authentication.
        if len (new_password) > 0:
            if not result:
                return jsonify({
                    "code": 404,
                    "message": "Utilisateur introuvable."
                })
            
            # Using bcrypt to check the old password.
            if not bcrypt.checkpw(old_password.encode('utf-8'), result[0].encode('utf-8')):
                return jsonify({
                    "code": 400,
                    "message": "Ancien mot de passe incorrect."
                })
            
            mfa = bool(mfa)
            # Hash the new password.
            new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            
            # Update the user's password and two-factor authentication in the database.
            cursor.execute("UPDATE users SET password = %s, 2fa = %s WHERE id = %s;", (new_password, mfa, current_user.id))
            conn.commit()
            return jsonify({
                "code": 200,
                "message": "Mot de passe modifié avec succès."
            })
        else:
            # Update the user's two-factor authentication in the database.
            cursor.execute("UPDATE users SET 2fa = %s WHERE id = %s;", (mfa, current_user.id))
            conn.commit()
            return jsonify({
                "code": 200,
                "message": "Authentification à deux facteurs modifiée avec succès."
            })
        
    except mysql.connector.Error as e:
        logging.error("Error while changing password: " + str(e))
        abort(500)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    
@user_data_bp.route('/dashboard/settings/change-user-infos', methods = ['POST'])
@login_required
def change_user_infos():
    """ 
    Change the user's informations.
    
    This function changes the user's informations in the database.
    
    Args:
        username (string): The user's name.
        email (string): The user's email.
        profilePicture (int): The user's profile picture.
        
    Returns:
        dict: The status message.
            - code (int): The status code.
                -> 200: The informations were changed.
                -> 201: A verification code was sent.
                -> 400: The email is already used.
                -> 404: The user was not found.
            - message (string): The status message.
            
    Raises:
        500: If there is an error while updating the informations in the database.
    """
    name = request.json.get('username')
    email = request.json.get('email')
    picture = request.json.get('profilePicture')

    conn = None
    cursor = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        picture = int(picture)
        if not picture in range(1,13):
            return jsonify({
                "code": 400,
                "message": "Image de profil invalide."
            })
        picture = "picture-" + str(picture)
        
        # Check if the user wanted to change the email or/and the profile picture.
        if email == current_user.email:
            # Update the user's name and profile picture in the database.
            cursor.execute("UPDATE users SET name = %s, picture = %s WHERE id = %s;", (name, picture, current_user.id))
            return jsonify({
                "code": 200,
                "message": "Informations modifiées avec succès."
            })
        else:
            # Check if the email is already used.
            cursor.execute("SELECT * FROM users WHERE email = %s;", (email,))
            result = cursor.fetchone()
            if result:
                return jsonify({
                    "code": 400,
                    "message": "Adresse mail déjà utilisée."
                })
            else:
                # Send a verification code to the user's email.
                if "2fa" not in session or session["2fa"]["expires"] < time.time():
                    # Generate a random secret key and a verification code.
                    secret_key = pyotp.random_base32()
                    totp = pyotp.TOTP(secret_key)
                    
                    session["2fa"] = {
                        "username": name,
                        "email": email,
                        "picture": picture,
                        "secret_key": secret_key,
                        "expires": time.time() + 300
                    }
                    
                    # Send the verification code to the user's email.
                    html = render_template('emails/2fa.html', name=name, code=totp.now())
                    send_mail(email, "Code de vérification - WORD QUEST", html)
                    return jsonify({
                        "code": 201,
                        "message": "Un code de vérification a été envoyé à votre adresse mail."
                    })         
                else:
                    # If a code was already sent, return an error.
                    return jsonify({
                        "code": 400,
                        "message": "Un code a déjà été envoyé."
                    })
            
    except mysql.connector.Error as e:
        logging.error("Error while changing user's informations: " + str(e))
        abort(500)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()    
            
@user_data_bp.route('/dashboard/settings/verify-email/<string:code>')
@login_required
def verify_email(code):
    """ 
    Verify the user's email, using the two-factor authentication.
    
    Args:
        code (string): The verification code.
    
    Returns:
        dict: The status message.
            - code (int): The status code.
                -> 200: The email was verified.
                -> 400: The code is expired.
                -> 400: The code is invalid.
            - message (string): The status message.
            
    Raises:
        500: If there is an error while updating the email in the database.
    """
    # Check if the code is expired.
    if "2fa" not in session or session["2fa"]["expires"] < time.time():
        return jsonify({
            "code": 400,
            "message": "Code expiré."
        })
    # Check if the code is valid.
    # Using pyotp to verify the code.
    totp = pyotp.TOTP(session["2fa"]["secret_key"])
    if not totp.verify(code, valid_window=10):
        return jsonify({
            "code": 400,
            "message": "Code invalide."
        })
    
    conn = None
    cursor = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        # Update the user's email in the database.
        cursor.execute("UPDATE users SET name = %s, email = %s, picture = %s WHERE id = %s;", (session["2fa"]["username"], session["2fa"]["email"], session["2fa"]["picture"], current_user.id))
        del session["2fa"]
        return jsonify({
            "code": 200,
            "message": "Adresse mail modifiée avec succès."
        })
        
    except mysql.connector.Error as e:
        logging.error("Error while verifying email: " + str(e))
        abort(500)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()    
            
@user_data_bp.route('/dashboard/settings/change-visibility/<int:visibility>', methods = ['POST'])
@login_required
def change_visibility(visibility):
    """
    Change the user's visibility.

    This function updates the visibility of the user in the database.

    Args:
        visibility (int): The user's visibility. 0 for private, 1 for public.

    Returns:
        dict: The status message.
            - code (int): The status code.
                -> 200: The visibility was changed successfully.
            - message (string): The status message.

    Raises:
        500: If there is an error while updating the visibility in the database.
    """
    conn = None
    cursor = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        # Check if the visibility is valid.
        visibility = 0 if visibility > 1 or visibility < 0 else visibility
        # Update the user's visibility in the database.
        cursor.execute("UPDATE users SET public = %s WHERE id = %s;", (visibility, current_user.id))
        conn.commit()
        return jsonify({
            "code": 200,
            "message": "Visibilité modifiée avec succès."
        })
        
    except mysql.connector.Error as e:
        logging.error("Error while changing visibility: " + str(e))
        abort(500)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
@user_data_bp.route('/dashboard/settings/delete-account', methods = ['POST'])
@login_required
def delete_account():
    """
    Delete the user's account.
    
    This function deletes the user's account from the database. It performs the following actions:
    1. Deletes the user's information from the 'users' table.
    2. Deletes any subscriptions related to the user from the 'subscriptions' table.
    3. Deletes any user statements related to the user from the 'user_statements' table.
    4. Deletes any lessons log related to the user from the 'lessons_log' table.
    5. Deletes any rewards related to the user from the 'rewards' table.
    6. Deletes any list content related to the user's lists from the 'list_content' table.
    7. Deletes any lessons related to the user's lists from the 'lessons' table.
    8. Deletes the user's lists from the 'lists' table.
    9. Commits the changes to the database.
    10. Logs out the user.
    
    Returns:
        dict: The status message.
            - code (int): The status code.
                -> 200: The account was deleted.
            - message (string): The status message.
            
    Raises:
        500: If there is an error while deleting the user's account from the database.
    """
    conn = None
    cursor = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        # Delete the user's account from the database.
        cursor.execute("DELETE FROM users WHERE id = %s;", (current_user.id,))
        cursor.execute("DELETE FROM subscriptions WHERE user_id = %s OR subscribed_to = %s;", (current_user.id, current_user.id))
        cursor.execute("DELETE FROM user_statements WHERE user_id = %s;", (current_user.id,))
        cursor.execute("DELETE FROM lessons_log WHERE user_id = %s;", (current_user.id,))
        cursor.execute("DELETE FROM rewards WHERE user_id = %s;", (current_user.id,))
        for list in current_user.get_lists():
            cursor.execute("DELETE FROM list_content WHERE list_id = %s;", (list["id"],))
            cursor.execute("DELETE FROM lessons WHERE list_id = %s;", (list["id"],))
            cursor.execute("DELETE FROM lists WHERE id = %s;", (list["id"],))
        conn.commit()
        logout_user()
        return jsonify({
            "code": 200,
            "message": "Compte supprimé avec succès."
        })
        
    except mysql.connector.Error as e:
        logging.error("Error while deleting account: " + str(e))
        if conn:
            conn.rollback()
        abort(500)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()