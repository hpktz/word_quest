from flask import Blueprint, render_template, redirect, url_for, jsonify, request, session, abort, make_response
from flask_login import login_user, login_required, logout_user, current_user
from root import *
import random as random
import datetime as datetime
import uuid as uuid
import json
from functools import wraps 

typefast_bp = Blueprint('typefast', __name__)

typefast_id = 7

class typeFast():
    def __init__(self, list_id, lesson_id, words):
        self.id = str(uuid.uuid4())
        self.list_id = list_id
        self.lesson_id = lesson_id
        self.words = words
        self.words_to_check = words
        self.time = str(datetime.datetime.now() + datetime.timedelta(minutes=2))
        self.start = str(datetime.datetime.now())
        
    def check_word(self, word):
        if self.time < str(datetime.datetime.now()) or len(self.words_to_check) == 0:
            return self._end_game()
        
        for index, word_to_check in enumerate(self.words_to_check):
            if word_to_check["word"] == word:
                self.words_to_check.pop(index)
                if len(self.words_to_check) == 0:
                    return self._end_game()
                time_passed = datetime.datetime.now() - datetime.datetime.strptime(self.start, '%Y-%m-%d %H:%M:%S.%f')
                time_passed = time_passed.total_seconds()    
                xp = round(((len(self.words) * 2) / time_passed)*10)
                return jsonify({
                    "code": 200,
                    "message": "Le mot a été trouvé avec succès!",
                    "result": {
                        "remaining": len(self.words_to_check),
                        "time": self.start,
                        "xp": xp,
                        "lost_lives": 0
                    }
                })

        return jsonify({
            "code": 404,
            "message": "Le mot n'a pas été trouvé!",
            "result": []
        })
        
    def get_remaning_time(self):
        return round((datetime.datetime.strptime(self.time, '%Y-%m-%d %H:%M:%S.%f') - datetime.datetime.now()).total_seconds())
        
    def get_words_checked(self):
        # Get the words that have been checked
        words = []
        for word in self.words:
            if word not in self.words_to_check:
                words.append(word)
        return words
        
    def _lose_life(self):
        conn = None
        cursor = None
        try:
            conn = create_connection()
            if current_user.get_lives() > 0:
                cursor.execute("INSERT INTO user_statements (user_id, transaction_type, transaction) VALUES (%s, 'lives', -1);", (current_user.id))
                conn.commit()

        except Exception as e:
            pass # Handle the exception
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        
    def _end_game(self):
        conn = None
        cursor = None
        try:
            conn = create_connection()  
            cursor = conn.cursor()
            cursor.execute("UPDATE lessons SET completed = 1 WHERE id = %s", (self.lesson_id,))
            
            time_passed = datetime.datetime.now() - datetime.datetime.strptime(self.start, '%Y-%m-%d %H:%M:%S.%f')
            time_passed = time_passed.total_seconds()
            xp = round(((len(self.words) * 2) / time_passed)*10)
                
            lives_to_lose = 1 if len(self.words_to_check) > 0 else 0
            while lives_to_lose > 0:
                self._lose_life()
                lives_to_lose -= 1
            
            cursor.execute("INSERT INTO lessons_log (user_id, lesson_id, xp, lost_lives, time) VALUES (%s, %s, %s, %s, %s)", (current_user.id, self.lesson_id, xp, lives_to_lose, time_passed))
            cursor.execute("INSERT INTO user_statements SET user_id= %s, transaction_type = 'xp', transaction = %s", ( current_user.id, xp))
            conn.commit()
            
            response = jsonify({
                "code": 201,
                "message": "Le jeu est terminé!",
                "result": {
                    "remaining": len(self.words_to_check),
                    "time": time_passed,
                    "xp": xp,
                    "lost_lives": lives_to_lose,
                }
            })
            response = make_response(response, 201)
            return response
        except Exception as e:
            print(e)
            return jsonify({
                "code": 500,
                "message": "Une erreur s'est produite!",
                "result": []
            }), 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def to_json(self): 
        return json.dumps(self, default=lambda o: o.__dict__) 

    @classmethod
    def from_json(cls, json_string):
        json_dict = json.loads(json_string)
        to_extract = cls(json_dict["list_id"], json_dict["lesson_id"], json_dict["words"])
        to_extract.id = json_dict["id"]
        to_extract.time = json_dict["time"]
        to_extract.words_to_check = json_dict["words_to_check"]
        to_extract.start = json_dict["start"]
        return to_extract    

def check_game(func):
    @wraps(func)
    def wrapper_function(session_id, *args, **kwargs):
        if 'game' in session:
            game = typeFast.from_json(session["game"])
            if session_id != game.id or game.time < str(datetime.datetime.now()):
                response = game._end_game()
                session["game"] = game.to_json()
                return response
            else:
                return func(session_id, *args, **kwargs)
        return jsonify({
            "code": 404,
            "message": "Le jeu n'a pas été trouvé!",
            "result": []
        })
    return wrapper_function

@typefast_bp.route('/dashboard/games/typefast/<int:list_id>')
@login_required
def index(list_id):
    # get the liste index from the user
    # print('hello')
    # print(current_user)
    # print('word')
    list_result = [l for l in current_user.get_lists() if l["id"] == list_id]
    if not list_result:
        abort(404)
    else:
        list_result = list_result[0]
    
    print(list_result)
    
    list_result["lessons"] = sorted(list_result["lessons"], key=lambda k: k['odr'])
    # Calculate the status of each game
    for index, game in enumerate(list_result["lessons"]):
        if index == 0 and game["lesson_id"] == typefast_id:
            game = typeFast(list_result["id"], game["id"], list_result["words"])
            id = game.id
            session['game'] = game.to_json()
            return redirect(url_for('typefast.start', session_id=id))
        elif index > 0 and list_result["lessons"][index-1]["completed"] == 1 and game["lesson_id"] == typefast_id:
            game = typeFast(list_result["id"], game["id"], list_result["words"])
            id = game.id
            session['game'] = game.to_json()
            return redirect(url_for('typefast.start', session_id=id))
    
    abort(404)
    

@typefast_bp.route('/dashboard/games/typefast/<string:session_id>')
def start(session_id):
    if 'game' in session:
        game = typeFast.from_json(session["game"])
        if session_id == game.id and game.time > str(datetime.datetime.now()):
            return render_template('games/typefast.html', 
                                   session_id=session_id, 
                                   list_id=game.list_id, 
                                   score=len(game.words_to_check), 
                                   max_score=len(game.words), 
                                   time=game.get_remaning_time(),
                                   words=game.get_words_checked()
                                   )
        return redirect(url_for('typefast.index', list_id=game.list_id))
    return redirect(url_for('main.index'))
    
@typefast_bp.route('/dashboard/games/typefast/<string:session_id>/check_word/<string:word>')
@check_game
def check_word(session_id, word):
    game = typeFast.from_json(session["game"])
    response = game.check_word(word)
    session["game"] = game.to_json()

    if response.status_code == 201:
        session.pop("game", None)

    return response