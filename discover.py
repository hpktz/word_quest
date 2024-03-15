"""
This module contains the discover blueprint, which is used to handle the discover routes of the application.

Imports:
    - flask: For handling the HTTP requests and responses.
    - flask_login: For the login_required decorator.
    - root: For the create_connection function.
    - random: For generating random numbers.
    - json: For parsing and stringifying JSON data.
    - SequenceMatcher: For comparing strings.
    - logging: For logging errors.

Blueprint:
    - discover_bp: The discover blueprint, which is used to handle the discover routes of the application.
"""
from flask import Blueprint, render_template, redirect, url_for, jsonify, request, session, abort
from flask_login import login_user, login_required, logout_user, current_user
from root import *
import random as random
import json
from difflib import SequenceMatcher
import logging

discover_bp = Blueprint('discover', __name__)
"""
The discover blueprint, which is used to handle the discover routes of the application.

Routes:
    - /dashboard/discover: The discover route, which is used to display the discover page.
    - /dashboard/list/like/<int:list_id>: The like_list route, which is used to like a list.
    - /dashboard/list/search/<string:search>: The search_list route, which is used to search for a list.
"""

@discover_bp.route('/dashboard/discover')
@login_required
def discover():
    """
    This route is used to display the discover page.
    
    Returns:
        render_template: The discover page.
    """
    user_list = current_user.get_lists() # Get the user's lists.
    user_lists_title = [lst['title'] for lst in user_list] # Get the user's lists' titles.
    user_words = [word['word'] for lst in user_list for word in lst['words']] # Get the user's words.
    
    all_lists = []
    conn = None
    cursor = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                lists.id AS list_id, 
                lists.initial_id AS list_initial, 
                lists.title AS list_title, 
                lists.public AS list_visibility, 
                lists.user_id AS list_user, 
                JSON_ARRAYAGG(JSON_OBJECT('word', list_content.word, 'type', list_content.word_type)) AS words, 
                COALESCE(like_counts.like_count, 0) AS like_count,
                CASE WHEN list_likes.user_id IS NULL THEN FALSE ELSE TRUE END AS user_in_like_list 
            FROM 
                lists 
            LEFT JOIN 
                list_content ON lists.id = list_content.list_id 
            LEFT JOIN 
                (SELECT list_id, COUNT(DISTINCT id) AS like_count FROM list_likes GROUP BY list_id) AS like_counts ON lists.id = like_counts.list_id 
            LEFT JOIN 
                list_likes ON lists.id = list_likes.list_id AND list_likes.user_id = %s 
            WHERE 
                lists.user_id != %s 
                AND lists.initial_id IS NULL
            GROUP BY 
                lists.id, lists.title;
            """, (current_user.id, current_user.id)) # Execute the SQL query to get all the lists from the database.
        columns = [column[0] for column in cursor.description]
        lists = cursor.fetchall()
        for lst in lists:
            # Get the list's data.
            result = dict(zip(columns, lst))
            if result["list_visibility"] == 0:
                continue
            
            # Retrieve the list's data.
            result["words"] = json.loads(result["words"])
            result["amount"] = random.choice([5, 8, 10]) if len(result["words"]) > 10 else len(result["words"]) # Get the amount of words to display.
            result["nb_words_not_displayed"] = len(result["words"]) - result["amount"] # Get the number of words not displayed.
            
            ############################
            # RECOMMENDATION ALGORITHM #
            ############################
            
            # Calculate the list's coefficient.
            result["coef"] = 0
            for title in user_lists_title:
                # Compare the list's title with the user's lists' titles.
                # Get the ratio of similarity between the list's title and the user's lists' titles.
                result["coef"] +=  SequenceMatcher(None, title, result["list_title"]).ratio() * 1
                
            for word in result['words']:
                # Compare the list's words with the user's words.
                # Get the ratio of similarity between the list's words and the user's words.
                result["coef"] +=  2 if word['word'] in user_words else 0
                
            result["words"] = result["words"][:result["amount"]] # Get the words to display.            
            result["coef"] +=  result["like_count"] * 0.1 # Add the list's like count to the coefficient.
            result["is_owner"] = not result["list_initial"]
            
            all_lists.append(result)
        
        all_lists = sorted(all_lists, key=lambda x: x['coef'], reverse=True) # Sort the lists by their coefficient.
        return render_template('dashboard/discover.html', all_lists = all_lists)
    except Exception as e:
        logging.error(e)
        abort(500)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        
@discover_bp.route('/dashboard/list/like/<int:list_id>', methods=['POST'])
@login_required
def like_list(list_id):
    """
    This route is used to like a list.
    
    Args:
        list_id (int): The list's id.
    
    Returns:
        dict: A JSON response containing the result of the operation. 
            - code (int): The status code of the response.
                -> 200: The list has been liked.
                -> 404: The list is not found.
                -> 500: An internal error occurred.
            - message (str): The message of the response.
    """
    conn = None
    cursor = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM lists WHERE id = %s", (list_id,)) # Execute the SQL query to get the list from the database.
        if not cursor.fetchone():
            return jsonify({'code': 404, 'message': 'Liste introuvable'})
        cursor.execute('SELECT * FROM list_likes WHERE user_id = %s AND list_id = %s', (current_user.id, list_id)) # Execute the SQL query to check if the user has already liked the list.
        # According to the result of the query, like or unlike the list.
        if cursor.fetchone():
            cursor.execute('DELETE FROM list_likes WHERE user_id = %s AND list_id = %s', (current_user.id, list_id)) # Execute the SQL query to unlike the list.
        else:
            cursor.execute('INSERT INTO list_likes (user_id, list_id) VALUES (%s, %s)', (current_user.id, list_id)) # Execute the SQL query to like the list.
        conn.commit()
        return jsonify({'code': 200, 'message': 'Liste likée'})
    except Exception as e:
        logging.error(e)
        return jsonify({'code': 500, 'message': 'Erreur interne'})
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
@discover_bp.route('/dashboard/list/search/<string:search>')
@login_required
def search_list(search):
    """ 
    This route is used to search for a list.
    
    Args:
        search (str): The search query.
        
    Returns:
        dict: A JSON response containing the result of the operation. 
            - code (int): The status code of the response.
                -> 200: The search has been performed.
                -> 404: No list found.
                -> 500: An internal error occurred.
            - message (str): The message of the response.
            - data (list): The data of the response.
    """
    conn = None
    cursor = None
    try: 
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                lists.id AS list_id,
                lists.title AS list_title, 
                users.name AS user_name,
                JSON_ARRAYAGG(
                    JSON_OBJECT('word', list_content.word, 'type', list_content.word_type)
                ) AS first_three_words
            FROM 
                lists 
            LEFT JOIN 
                users ON lists.user_id = users.id 
            LEFT JOIN 
                list_content ON lists.id = list_content.list_id 
            WHERE 
                lists.title LIKE %s 
                AND lists.public = 1 
                AND lists.initial_id IS NULL
            GROUP BY 
                lists.id, users.name 
            ORDER BY 
                lists.title 
            LIMIT 10
        """, (search + '%',)) # Execute the SQL query to search for the list in the database.
        columns = [column[0] for column in cursor.description]
        lists = cursor.fetchall()
        if not lists:
            return jsonify({'code': 404, 'message': 'Aucune liste trouvée'}), 404
        results = []
        for lst in lists:
            result = dict(zip(columns, lst))
            result["first_three_words"] = json.loads(result["first_three_words"]) # Parse the first three words of the list.
            results.append(result)
        
        return jsonify({'code': 200, 'message': 'Recherche effectuée', 'data': results})
    except Exception as e:
        logging.error(e)
        return jsonify({'code': 500, 'message': 'Erreur interne'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        