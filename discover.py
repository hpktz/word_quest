from flask import Blueprint, render_template, redirect, url_for, jsonify, request, session, abort
from flask_login import login_user, login_required, logout_user, current_user
from root import *
import random as random
import json
from difflib import SequenceMatcher
import logging

discover_bp = Blueprint('discover', __name__)

@discover_bp.route('/dashboard/discover')
@login_required
def discover():
    user_list = current_user.get_lists()
    # Get only the word : user_list->words->word
    user_lists_title = [lst['title'] for lst in user_list]
    user_words = [word['word'] for lst in user_list for word in lst['words']]
    
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
                COALESCE(COUNT(DISTINCT routes_log.id), 0) AS page_views, 
                CASE WHEN list_likes.user_id IS NULL THEN FALSE ELSE TRUE END AS user_in_like_list 
            FROM 
                lists 
            LEFT JOIN 
                list_content ON lists.id = list_content.list_id 
            LEFT JOIN 
                (SELECT route, COUNT(DISTINCT id) AS id FROM routes_log GROUP BY route) AS routes_log ON routes_log.route = CONCAT('/dashboard/profile/list/', lists.id)
            LEFT JOIN 
                (SELECT list_id, COUNT(DISTINCT id) AS like_count FROM list_likes GROUP BY list_id) AS like_counts ON lists.id = like_counts.list_id 
            LEFT JOIN 
                list_likes ON lists.id = list_likes.list_id AND list_likes.user_id = %s 
            WHERE 
                lists.user_id != %s 
            GROUP BY 
                lists.id, lists.title;
            """, (current_user.id, current_user.id))
        columns = [column[0] for column in cursor.description]
        lists = cursor.fetchall()
        print(lists)
        for lst in lists:
            result = dict(zip(columns, lst))
            result["words"] = json.loads(result["words"])
            result["coef"] = 0
            for title in user_lists_title:
                result["coef"] +=  SequenceMatcher(None, title, result["list_title"]).ratio() * 1
                
            for word in result['words']:
                result["coef"] +=  2 if word['word'] in user_words else 0
            
            result["coef"] +=  result["like_count"] * 0.1
            result["coef"] +=  result["page_views"] * 0.05
            print(int(result["list_id"]))
            result["is_owner"] = not result["list_initial"]
            
            all_lists.append(result)
        
        all_lists = sorted(all_lists, key=lambda x: x['coef'], reverse=True)
        return render_template('dashboard/discover.html', all_lists = all_lists)
    except Exception as e:
        logging.error(e)
        abort(500)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        
@discover_bp.route('/dashboard/list/like/<int:list_id>')
@login_required
def like_list(list_id):
    conn = None
    cursor = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM lists WHERE id = %s", (list_id,))
        if not cursor.fetchone():
            return jsonify({'code': 404, 'message': 'Liste introuvable'})
        cursor.execute('SELECT * FROM list_likes WHERE user_id = %s AND list_id = %s', (current_user.id, list_id))
        if cursor.fetchone():
            cursor.execute('DELETE FROM list_likes WHERE user_id = %s AND list_id = %s', (current_user.id, list_id))
        else:
            cursor.execute('INSERT INTO list_likes (user_id, list_id) VALUES (%s, %s)', (current_user.id, list_id))
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
    conn = None
    cursor = None
    try: 
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
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
            GROUP BY 
                lists.id, users.name 
            ORDER BY 
                lists.title 
            LIMIT 10
        """, (search + '%',))
        columns = [column[0] for column in cursor.description]
        lists = cursor.fetchall()
        if not lists:
            return jsonify({'code': 404, 'message': 'Aucune liste trouvée'}), 404
        results = []
        for lst in lists:
            result = dict(zip(columns, lst))
            result["first_three_words"] = json.loads(result["first_three_words"])
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
        