from flask import Blueprint, render_template, redirect, url_for, jsonify, request, session, abort
from flask_login import login_user, login_required, logout_user, current_user
from root import *
import random as random
import datetime as datetime
import uuid as uuid

hangman_bp = Blueprint('hangman', __name__)

hangman_id = 2

class hangman():
    def __init__(self, words, lives):
        self.id = uuid.uuid4()
        self.words = words
        self.lives = lives
        self.time = datetime.datetime.now() + datetime.timedelta(minutes=1) + datetime.timedelta(seconds=4)
        self.word = None
        self.hintCount = 0
        self.lettersDiscoverd = []
        
        # Etc ... (xp, score, etc)
    
    def checking_letter(self):
        pass
    
    def ask_hint(self):
        pass
    
    def _lose_life(self):
        conn = None
        cursor = None
        try:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user_statements (user_id, transaction_type, transaction) VALUES (%s, 'lives', -1);", (current_user.id))
            conn.commit()
        except Exception as e:
            pass # Handle the exception
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                
    def _end_lesson(self):
        conn = None
        cursor = None
        try:
            conn = create_connection()  
            cursor = conn.cursor()
            cursor.execute("UPDATE lessons SET completed = 1 WHERE id = %s", (self.id,))
            cursor.execute("INSERT INTO lessons_log (user_id, lesson_id, xp, lost_lives, time) VALUES (%s, %s, %s, %s, %s)", (current_user.id, self.id, xp, self.lives, time))
            conn.commit()
        except Exception as e:
            pass
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        # Si le jouer a fait trop de fautes, on lui fait perdre une vie
        # Ainsi tu appelles : self._lose_life()

    # Etc ...
    
    

@hangman_bp.route('/dashboard/games/hangman/<int:list_id>')
@login_required
def index(list_id):
    # get the liste index from the user
    list_result = [l for l in current_user.lists if l["id"] == list_id]
    if not list_result:
        abort(404)
    else:
        list_result = list_result[0]
    
    
    list_result["lessons"] = sorted(list_result["lessons"], key=lambda k: k['odr'])
    # Calculate the status of each game
    for index,game in enumerate(list_result["lessons"]):
        if index == 0 and game["lesson_id"] == hangman_id:
            session['game'] = hangman(list_result["words"], 5)
            return redirect(url_for('hangman.start', session_id=session['game'].id))
        elif index > 0 and list_result["lessons"][index-1]["completed"] == 1 and game["lesson_id"] == hangman_id:
            session['game'] = hangman(list_result["words"], 5)
            return redirect(url_for('hangman.start', session_id=session['game'].id))
    
    abort(404)
    
@hangman_bp.route('/dashboard/games/hangman/session/<string:session_id>')
def start(session_id):
    if 'game' in session and str(session['game'].id) == str(session_id):
        return render_template('games/hangman.html')
    else:
        abort(404)
        
@hangman_bp.route('/dashboard/games/hangman/session/<string:session_id>/route', methods=['POST'])
def route(session_id):
    if 'game' in session and str(session['game'].id) == str(session_id):
        data = request.get_json()
        session["game"].mymethod(data)
        return jsonify({
            "code": 200,
            "message": "ok",
            "result": []
        })
    else:
        return jsonify({
            "code": 404,
            "message": "not found",
            "result": []
        })
