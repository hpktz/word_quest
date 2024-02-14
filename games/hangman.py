from flask import Blueprint, render_template, redirect, url_for, jsonify, request, session, abort
from flask_login import login_user, login_required, logout_user, current_user
from root import *
import random as random
import datetime as datetime
import uuid as uuid
import json
from functools import wraps 

hangman_bp = Blueprint('hangman', __name__)

hangman_id = 2

class hangman():
    def __init__(self, list_id, lesson_id, words):
        self.id = str(uuid.uuid4())
        self.list_id = list_id
        self.lesson_id = lesson_id
        self.words = words
        self.words2 = []
        self.time = str(datetime.datetime.now() + datetime.timedelta(minutes=1) + datetime.timedelta(seconds=5))
        self.word = None
        self.hintCount = 0
        self.goodLetters = []
        self.badLetters = []
        self.xp = 0
        self.xpmax = len(self.words) * 5
        self.xpTotal = 0
        


    def new_word(self):
        self.xpTotal += self.xp
        self.xp = 5
        self.xp = 5
        self.total_xp = 0
        self.xpmax = len(self.words) * 5

    def new_word(self):
        self.xpTotal += self.xp
        self.xp = 5
        if len(self.words) > 0:
            self.word = random.choice(self.words)
            self.words2.append(self.word)
            for i in range(len(self.words)):
                if self.words[i] == self.word:
                    del(self.words[i])
                    break
            return jsonify({
                "code": 200,
                "message": "ok",
                "result": self.word,
                "xptot": self.xpTotal
            })
        else:
            self.words += self.words2
            self.words2 = []
            return jsonify({
                "code": 404,
                "message": "not found",
                "result": [],
                "xptot": self.xpTotal
                
            })

    def checking_letter(self, letter):
        all_letters = self.goodLetters + self.badLetters
        for i in all_letters:
            if i == letter:
                return jsonify({
                "code": 200,
                "message": "ok",
                "result": "already touch"
                })
        if letter in self.word["word"]:
            self.goodLetters.append(letter)
            return jsonify({
                "code": 200,
                "message": "ok",
                "result": {"good": self.goodLetters,
                           "bad": self.badLetters,
                           "xp": self.xp,
                           "True": True}
            })
        else:
            self.badLetters.append(letter)
            if len(self.badLetters) < 2:
                self.xp = 5
            if len(self.badLetters) >= 2 and len(self.badLetters) < 4:
                self.xp = 3
            elif len(self.badLetters) == 4:
                self.xp = 2
            elif len(self.badLetters) == 5:
                self.xp = 1
            elif len(self.badLetters) == 6:
                self.xp = 0
            return jsonify({
                "code": 200,
                "message": "ok",
                "result": {"good": self.goodLetters,
                           "bad": self.badLetters,
                           "xp": self.xp,
                           "True": False}
            })
    
    def reset_letter(self):
        self.badLetters = []
        self.goodLetters = []
        self.hintCount = 0
        self.total_xp += self.xp
        return jsonify({
                "code": 200,
                "message": "ok",
                "result": {"good": [],
                           "bad": []}
            })

    def ask_hint(self):
        self.hintCount += 1
        if self.hintCount == 1:
            self.xp = 4 if self.xp > 4 else self.xp
            return jsonify({
                "code": 200,
                "message": "ok",
                "result": {"indice": self.word['type'],
                            "title": 'Type du mot',
                            "xp": self.xp}

            })
        if self.hintCount == 2:
            self.xp = 3 if self.xp > 3 else self.xp
            if self.word['trans_examples'] != []:
                return jsonify({
                    "code": 200,
                    "message": "ok",
                    "result": { "indice": random.choice(self.word['trans_examples']),
                                "title" : 'Phrase en francais',
                                "xp": self.xp}
                })
            else:
                self.hintCount += 1
        if self.hintCount == 3:
            self.xp = 2 if self.xp > 2 else self.xp
            return jsonify({
                "code": 200,
                "message": "ok",
                "result": { "indice": self.word['trans_word'],
                           "title" : 'Le mot en francais',
                           "xp": self.xp}
            })
        else:
            return None
        
    def reload(self):
        self.words += self.words2
        self.time = str(datetime.datetime.now() + datetime.timedelta(minutes=1) + datetime.timedelta(seconds=5))
        self.words2 = []
        self.badLetters = []
        self.goodLetters = []
        self.hintCount = 0
        self.xp = 0
        self.xpTotal = 0

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
                
    def _end_lesson(self):
        conn = None
        cursor = None
        try:
            conn = create_connection()  
            cursor = conn.cursor()
            cursor.execute("UPDATE lessons SET completed = 1 WHERE id = %s", (self.lesson_id,))
            if self.time < str(datetime.datetime.now()):
                time = 65
            else:
                time = 60 - int((datetime.datetime.strptime(self.time, '%Y-%m-%d %H:%M:%S.%f') - datetime.datetime.now()).total_seconds())
            lives_to_lose = 0
            if self.xp / self.xpmax < 0.7:
                lives_to_lose = 1
            if self.xp / self.xpmax < 0.4:
                lives_to_lose = 2
            if self.xp / self.xpmax < 0.2:
                lives_to_lose = 3
                
            while lives_to_lose > 0:
                self._lose_life()
                lives_to_lose -= 1
            
            print(current_user.id, self.id, self.xp, lives_to_lose, time)
            cursor.execute("INSERT INTO lessons_log (user_id, lesson_id, xp, lost_lives, time) VALUES (%s, %s, %s, %s, %s)", (current_user.id, self.lesson_id, self.total_xp, lives_to_lose, time))
            cursor.execute("INSERT INTO user_statements SET user_id= %s, transaction_type = 'xp', transaction = %s", ( current_user.id, self.total_xp))
            conn.commit()
        except Exception as e:
            print(e)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        # Si le jouer a fait trop de fautes, on lui fait perdre une vie
        # Ainsi tu appelles : self._lose_life()
    
        # Autres méthodes
                
    def to_json(self):
        """
        Convert the list to JSON.

        Returns:
            dict: The list in JSON.
        """
        return json.dumps({
            "id": self.id,
            "list_id": self.list_id,
            "lesson_id": self.lesson_id,
            "words": self.words,
            "words2": self.words2,
            "time": self.time,
            "word": self.word,
            "hintCount": self.hintCount,
            "goodLetters": self.goodLetters,
            "badLetters": self.badLetters,
            "xp": self.xp,
            "xpmax": self.xpmax,
            "xpTotal": self.xpTotal
        })
        
    @classmethod
    def from_json(cls, json_string):
        """
        Create a list from JSON.

        Args:
            json_data (dict): The list in JSON.

        Returns:
            WordList: The list.
        """
        data = json.loads(json_string)
        to_extract= cls(data["list_id"], data["lesson_id"], data["words"])
        to_extract.id= data["id"]
        to_extract.words= data["words"]
        to_extract.words2= data["words2"]
        to_extract.time= data["time"]
        to_extract.word= data["word"]
        to_extract.hintCount= data["hintCount"]
        to_extract.goodLetters= data["goodLetters"]
        to_extract.badLetters= data["badLetters"]
        to_extract.xp = data["xp"]
        to_extract.xpmax = data["xpmax"]
        to_extract.xpTotal = data["xpTotal"]


        return to_extract
    
    
    
def check_game(func):
    @wraps(func)
    def wrapper_function(*args, **kwargs):
        if 'game' in session:
            game = hangman.from_json(session["game"])
            print(game.time)
            if game.time < str(datetime.datetime.now()):
                session["game"] = game.to_json()
                return jsonify({
                    "code": 404,
                    "message": "not found",
                    "result": []
                })
            else:
                return func(*args, **kwargs)
        return jsonify({
            "code": 404,
            "message": "not found",
            "result": []
        })
    return wrapper_function
    

@hangman_bp.route('/dashboard/games/hangman/<int:list_id>')
@login_required
def index(list_id):
    list_result = [l for l in current_user.get_lists() if l["id"] == list_id]
    if not list_result:
        abort(404)
    else:
        list_result = list_result[0]
    
    list_result["lessons"] = sorted(list_result["lessons"], key=lambda k: k['odr'])
    # Calculate the status of each game
    for index, game in enumerate(list_result["lessons"]):
        if index == 0 and game["lesson_id"] == hangman_id:
            game = hangman(list_result["id"], game["id"], list_result["words"])
            id = game.id
            session['game'] = game.to_json()
            return redirect(url_for('hangman.start', session_id=id))
        elif index > 0 and list_result["lessons"][index-1]["completed"] == 1 and game["lesson_id"] == hangman_id:
            session['game'] = hangman(list_result["words"], 5).to_json()
            return redirect(url_for('hangman.start', session_id=session['game']["id"], list_id=list_id))
    
    abort(404)
    
@hangman_bp.route('/dashboard/games/hangman/session/<string:session_id>')
def start(session_id):
    game = hangman.from_json(session["game"])
    game.reload()
    if 'game' in session and str(game.id) == str(session_id):
        session["game"] = game.to_json()
        return render_template('games/hangman.html')
    else:
        abort(404)
     
@hangman_bp.route('/dashboard/games/hangman/session/<string:session_id>/ask_letter', methods=['POST'])
@check_game
def route(session_id):
    game = hangman.from_json(session["game"])
    if 'game' in session and str(game.id) == str(session_id):
        data = request.get_json()
        game.ask_letter()
        session["game"] = game.to_json()
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

@hangman_bp.route('/dashboard/games/hangman/session/ask_word')
@check_game
def select_word():
    game = hangman.from_json(session["game"])
    result = game.new_word()
    session["game"] = game.to_json()
    return result

@hangman_bp.route('/dashboard/games/hangman/session/check_letter/<string:e>')
@check_game
def check(e):
    game = hangman.from_json(session["game"])
    result = game.checking_letter(e)
    session["game"] = game.to_json()
    return result


@hangman_bp.route('/dashboard/games/hangman/session/reset')
@check_game
def reset():
    game = hangman.from_json(session["game"])
    result = game.reset_letter()
    session["game"] = game.to_json()
    return result

@hangman_bp.route('/dashboard/games/hangman/session/askhint')
@check_game
def new_hint():
    game = hangman.from_json(session["game"])
    result = game.ask_hint()
    session["game"] = game.to_json()
    return result

@hangman_bp.route('/dashboard/games/hangman/session/finish')
def finish():
    game = hangman.from_json(session["game"])
    game._end_lesson()
    session.pop('game', None)
    return jsonify({
        "code": 200,
        "message": "ok",
        "result": []
    })