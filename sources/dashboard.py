"""
This module contains the main routes for the application.

Imports:
    - flask: For handling requests and responses.
    - flask_login: For handling user sessions.
    - profanity_detector: For detecting the presence of profanity in a text.
    - root: The root module of the application.
    - json: For parsing and generating JSON data.
    - datetime: For handling dates and times.
    - random: For generating random numbers.
    - logging: For logging errors and other information.
    - re: For handling regular expressions.
    - uuid: For generating unique identifiers.

Blueprint:
    - main_bp: The blueprint for the main routes of the application.
"""
from flask import Blueprint, render_template, redirect, url_for, jsonify, request, session, abort
from flask_login import login_user, login_required, logout_user, current_user
from profanity import profanity_detector
from root import *
import json
from datetime import datetime, timedelta
import random as random
import logging
import re
import uuid

main_bp = Blueprint('main', __name__)
"""
The blueprint for the main routes of the application.

Attributes:
    - main_bp: The blueprint for the main routes of the application.
    
Routes:
    - /dashboard: To display the dashboard page.
    - /dashboard/lives/purchase: To purchase lives for the current user.
    - /dashboard/games/<int:list_id>: To retrieve the game trail for a given list ID.
    - /dashboard/manage/<int:list_id>: To render the manage page for a given list ID.
    - /dashboard/manage/update/<int:list_id>: To update list information in the database.
    - /dashboard/delete/<int:list_id>: To delete a list and its associated data from the database.    
    - /dashboard/list/get_link/<int:list_id>: To get the link to a list.
"""

@main_bp.route('/dashboard')
@login_required
def index():
    """
    Render the dashboard page with user statistics and information.

    Returns:
        flask.Response: The rendered template for the dashboard page.
        
    Raises:
        gem (int): The updated number of gems set to 0.
        lives (int): The updated number of lives set to 0.
    """
    
    # Check if the user is coming from the create page
    new_list_param = request.args.get('new_list')
    is_new_list = new_list_param and new_list_param.lower() == 'true'

    # Calculate the start and end date of the user's journey
    lists = current_user.get_lists()
    if lists:
        start_date = min(datetime.strptime(str(lst["created_at"]), "%d/%m/%Y") for lst in lists)
        start_date = start_date.date().strftime("%Y-%m-%d")

        end_date = max(datetime.strptime(str(lst["created_at"]), "%d/%m/%Y") for lst in lists)    
        end_date = end_date.date().strftime("%Y-%m-%d")
    else:
        start_date = datetime.now().date().strftime("%Y-%m-%d")
        end_date = datetime.now().date().strftime("%Y-%m-%d")

    # Calculate the progress of each list
    for lst in lists:
        progress = sum(1 for lesson in lst["lessons"] if lesson["completed"] == 1)
        lst["progress"] = round((progress / len(lst["lessons"]) * 100), 0) if progress != 0 else 5 

    # Retrieve a random daytime tip
    with open(str(os.getenv("DIRECTORY_PATH")) + 'static/daytime-tips.json') as json_file:
        tips = json.load(json_file)

    tip = tips[random.randint(0, len(tips) - 1)]

    conn = None
    cursor = None    
    try:
        conn = create_connection()
        cursor = conn.cursor()
        # Retrieve the user's amount of gems, lives and XP
        cursor.execute("SELECT SUM(CASE WHEN transaction_type = 'gems' THEN transaction ELSE 0 END) \
                AS sum_gems, SUM(CASE WHEN transaction_type = 'lives' THEN transaction ELSE 0 END) \
                AS sum_lives, MAX(CASE WHEN transaction_type = 'lives' THEN created_at ELSE 0 END) \
                AS last_live, SUM(CASE WHEN transaction_type = 'xp' THEN transaction ELSE 0 END) AS sum_xp \
                FROM user_statements WHERE user_id = %s ORDER BY created_at DESC LIMIT 1;", (current_user.id,))
        user_statement = cursor.fetchone()
        gems = user_statement[0]
        lives = user_statement[1]
        lives_time = user_statement[2]
        life_time = None
        xp = user_statement[3]
        
        # Checking if the user is eligible for potential news lives
        print(lives_time)
        if lives != 5:
            life_time = datetime.strptime(str(lives_time), "%Y-%m-%d %H:%M:%S")
            life_time = life_time + timedelta(minutes=15)
            while life_time < datetime.now() and lives < 5:
                cursor.execute("INSERT INTO user_statements (user_id, transaction_type, transaction)\
                    VALUES (%s, 'lives', 1);", (current_user.id,))
                lives += 1
                life_time = life_time + timedelta(minutes=15)
                lives_time = datetime.now()
                    
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error("Error while fetching user statements: " + str(e), exc_info=True)
        gems = 0
        lives = 0
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        
    # Sort the lists by ID in descending order
    lists = sorted(lists, key=lambda k: k['id'], reverse=True)
    new_list_id = lists[0]["id"] if is_new_list else None
    
    hearts_message = True if request.args.get('hearts_message') else False
    
    lives_time = datetime.now()
    if not life_time:
        life_time = datetime.now()     
        
    if 'path_finished' in session:
        gifts = session['path_finished']
        session.pop('path_finished', None)
    else:
        gifts = False  
    
    print(gems)
    return render_template(
        'dashboard/dashboard.html', 
        daytime_tip=tip, 
        lists=lists, 
        start_date=start_date, 
        end_date=end_date,
        gems=gems, 
        lives=lives, 
        lives_time=lives_time.timestamp(), 
        lives_end=life_time.timestamp(),
        xp=xp,
        new_list_id=new_list_id, 
        gifts=gifts,
        hearts_message=hearts_message
    )
    
@main_bp.route('/dashboard/lives/purchase', methods=['POST'])
@login_required
def purchase_lives():
    """
    Purchase lives for the current user.

    Returns:
        dict: A dictionary containing the response code and updated lives and gems count.
            - code (int): The response code. 200 for success, 400 for failure.
                -> 200: The lives were successfully purchased.
                -> 400: The lives could not be purchased.
            - lives (int): The updated number of lives.
            - gems (int): The updated number of gems.
            
    Raises:
        500: If an error occurs while fetching the user statements.
    """
    conn = None
    cursor = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        # Retrieve the user's amount of gems and lives
        cursor.execute("SELECT SUM(CASE WHEN transaction_type = 'gems' THEN transaction ELSE 0 END) AS gems, SUM(CASE WHEN transaction_type = 'lives' THEN transaction ELSE 0 END) AS lives FROM user_statements WHERE user_id = %s;", (current_user.id,))
        user_statement = cursor.fetchone()
        gems = user_statement[0]
        lives = user_statement[1]
        # Check if the user has enough gems and lives
        if gems < 200 or lives == 5:
            return jsonify({"code": 400})
        else:
            # Purchase the lives
            cursor.execute("INSERT INTO user_statements (user_id, transaction_type, transaction) VALUES (%s, 'lives', 1), (%s, 'gems', -200);", (current_user.id, current_user.id))
            return jsonify({"code": 200, "lives": lives + 1, "gems": gems - 200})
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error("Error while fetching user statements: " + str(e), exc_info=True)
        abort(500)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@main_bp.route('/dashboard/games/<int:list_id>')
@login_required
def list(list_id):
    """
    Retrieve the game trail for a given list ID.

    Args:
        list_id (int): The ID of the list.

    Returns:
        flask.Response: The rendered template for the game trail.
   
    Raises:
        flask.render_template: The rendered template for the game trail.
    """
    try:
        # Retrieve the list and its associated games
        list_result = [l for l in current_user.get_lists() if l["id"] == list_id][0]  
        games_result = []

        with open(str(os.getenv("DIRECTORY_PATH")) + 'static/games-data.json') as json_file:
            games_data = json.load(json_file)

        status = None
        # Sort the games by order
        list_result["lessons"] = sorted(list_result["lessons"], key=lambda k: k['odr'])
        # Calculate the status of each game
        for game in list_result["lessons"]:
            game_data = [g for g in games_data if g["id"] == game["lesson_id"]][0]
            if game["completed"] == 1:
                status = "completed"
            elif status == "waiting":
                status = "blocked"
            elif status == "blocked":
                status = status
            else:
                status = "waiting"

            game_result = {
                "id": game["id"],
                "list_id": list_result["id"],
                "lesson_id": game["lesson_id"],
                "ord": game["odr"],
                "name": game_data["name"],
                "short_desc": game_data["short_desc"],
                "img": game_data["img"],
                "url": game_data["url"],
                "status": status,
                "completed": game["completed"]
            }
            games_result.append(game_result)
            
        return render_template('dashboard/content/game-trail-template.html', list=list_result, games=games_result)
    except Exception as e:
        logging.error("Error while fetching game trail: " + str(e), exc_info=True)
        return render_template('dashboard/content/game-trail-empty-template.html')

@main_bp.route('/dashboard/manage/<int:list_id>')
def manage(list_id):
    """Render the manage page for a given list ID.

    Args:
        list_id (int): The ID of the list.

    Returns:
        flask.Response: The rendered template for the manage page.

    Raises:
        flask.render_template: The rendered template for the manage page.
    """
    # Retrieve the list and its associated games
    try:
        list_result = [l for l in current_user.get_lists() if l["id"] == list_id][0]
        list_result["lessons"] = sorted(list_result["lessons"], key=lambda k: k['odr'])
        if list_result:
            return render_template('dashboard/content/manage-list.html', list=list_result), 200
        abort(404)
    except Exception as e:
        logging.error("Error while fetching list: " + str(e), exc_info=True)
        abort(500)
        
@main_bp.route('/dashboard/manage/update/<int:list_id>', methods=['POST'])
def update(list_id):
    """Update the name of a list in the database.

    Args:
        list_id (int): The ID of the list to be updated.

    Returns:
        flask.Response: A redirect response to the main index page.

    Raises:
        flask.redirect: A redirect response to the main index page.
    """
    # Update the name of the list
    conn = None
    cursor = None
    try:
        name = request.json.get('name')
        description = request.json.get('description')
        time  = int(request.json.get('time'))
        xp = int(request.json.get('xp'))
        game = int(request.json.get('game'))
        reminder = request.json.get('reminder')
        stats = request.json.get('stats')
        public = request.json.get('public')
        
        regex = re.compile(r'^[a-zA-Z0-9#\'\s,.!?À-ÿ]+$')
        if not regex.match(name):
            return jsonify({"code": 400, "message": "Caractères invalides"})
        
        if len(description) > 0 and not regex.match(description):
            return jsonify({"code": 400, "title": "Bad request", "message": "Caractères invalides"})
        
        if len(name) > 50 or len(description) > 500:
            return jsonify({"code": 400, "message": "Trop de caractères"})
        
        if len(name) == 0:
            return jsonify({"code": 400, "message": "Nom invalide"})
        
        if profanity_detector(name) or profanity_detector(description):
            return jsonify({"code": 400, "title": "Bad request", "message": "Contenu inapproprié"})
        
        time_normalized = [1, 3, 5]
        xp_normalized = [10, 20, 30]
        game_normalized = [1, 2, 3]
        
        if not isinstance(reminder, bool) or not isinstance(stats, bool) or not isinstance(public, bool)\
        or not time in time_normalized or not xp in xp_normalized or not game in game_normalized:
            return jsonify({"code": 400, "message": "Les valeurs ne sont pas valides. Veuillez réessayer."})
    
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE lists SET title = %s, description = %s, tgt_time = %s, tgt_xp = %s, tgt_games = %s, notif_remind = %s, notif_stats = %s, public = %s WHERE id = %s", (name, description, time, xp, game, reminder, stats, public, list_id))
        conn.commit()
    
        return jsonify({"code": 200, "message": "Liste mise à jour avec succès."})
    except Exception as e:
        logging.error("Error while updating list: " + str(e), exc_info=True)
        return jsonify({"code": 500, "message": "Une erreur s'est produite lors de la mise à jour de la liste. Veuillez réessayer plus tard."})
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@main_bp.route('/dashboard/delete/<int:list_id>', methods=['POST'])
@login_required
def delete(list_id):
    """Delete a list and its associated data from the database.

    Args:
        list_id (int): The ID of the list to be deleted.

    Returns:
        flask.Response: A redirect response to the main index page.

    Raises:
        flask.redirect: A redirect response to the main index page.
    """
    conn = None
    cursor = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        # Delete the list and its associated data
        cursor.execute("DELETE FROM lists WHERE id = %s", (list_id,))
        cursor.execute("DELETE FROM lessons WHERE list_id = %s", (list_id,))
        cursor.execute("DELETE FROM list_content WHERE list_id = %s", (list_id,))
        conn.commit()
        return redirect(url_for('main.index'))
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error("Error while deleting list: " + str(e), exc_info=True)
        return redirect(url_for('main.index'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close() 
            
            
@main_bp.route('/dashboard/list/get_link/<int:list_id>')
@login_required
def get_link(list_id):
    """Copy the link to a list to the clipboard.

    Args:
        list_id (int): The ID of the list.

    Returns:
        flask.Response: A redirect response to the main index page.

    Raises:
        flask.redirect: A redirect response to the main index page.
    """
    # Check if the list is one of the user's lists
    list = [l for l in current_user.get_lists() if l["id"] == list_id][0]
    if list:
        if list["shared_token"] and list["shared_expires"] > datetime.now():
            link = "/dashboard/list/copy_link/" + list["shared_token"]
            return jsonify({"code": 200, "message": "Liste déjà partagée.", "link": link})
        else:
            shared_token = str(uuid.uuid4())
            shared_expires = (datetime.now() + timedelta(minutes=60))
            conn = None
            cursor = None
            try:
                conn = create_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE lists SET shared_token = %s, shared_expires = %s WHERE id = %s", (shared_token, shared_expires, list_id))
                conn.commit()
                link = "/dashboard/list/copy_link/" + shared_token
                return jsonify({"code": 200, "message": "Liste partagée avec succès.", "link": link})
            except Exception as e:
                if conn:
                    conn.rollback()
                logging.error("Error while copying link: " + str(e), exc_info=True)
                return jsonify({"code": 500, "message": "Une erreur s'est produite lors de la copie du lien. Veuillez réessayer plus tard."})
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
    else:
        return jsonify({"code": 400, "message": "Liste introuvable."})
