from flask import Blueprint, render_template, redirect, url_for, jsonify, request, session, abort
from flask_login import login_user, login_required, logout_user, current_user
from root import *
import random as random
import datetime as datetime
import uuid as uuid
import json

hangman_bp = Blueprint('hangman', __name__)

hangman_id = 2

class hangman():
    def __init__(self, words, lives):
        self.id = str(uuid.uuid4())
        self.words = words
        self.words2 = []
        self.lives = lives
        self.time = str(datetime.datetime.now() + datetime.timedelta(minutes=1) + datetime.timedelta(seconds=4))
        self.word = None
        self.hintCount = 0
        self.goodLetters = []
        self.badLetters = []
        self.xp = 5
        self.xpmax = len(self.words) * 5
        


    def new_word(self):
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
                "test": self.words2
            })
        else:
            self.words += self.words2
            self.words2 = []
            return jsonify({
                "code": 404,
                "message": "not found",
                "result": [],
                "test": self.words2
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
                            "title": 'Type du mot'}

            })
        if self.hintCount == 2:
            self.xp = 3 if self.xp > 3 else self.xp
            if self.word['trans_examples'] != []:
                return jsonify({
                    "code": 200,
                    "message": "ok",
                    "result": { "indice": random.choice(self.word['trans_examples']),
                                "title" : 'Phrase en francais'}
                })
            else:
                self.hintCount += 1
        if self.hintCount == 3:
            self.xp = 2 if self.xp > 2 else self.xp
            return jsonify({
                "code": 200,
                "message": "ok",
                "result": { "indice": self.word['trans_word'],
                           "title" : 'Le mot en francais'}
            })
        else:
            return None
        
            

    def reload(self):
        self.words += self.words2
        self.words2 = []
        self.badLetters = []
        self.goodLetters = []
        self.hintCount = 0

    
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
    
        # Autres méthodes
                
    def to_json(self):
        """
        Convert the list to JSON.

        Returns:
            dict: The list in JSON.
        """
        return json.dumps({
            "id": self.id,
            "words": self.words,
            "words2": self.words2,
            "lives": self.lives,
            "time": self.time,
            "word": self.word,
            "hintCount": self.hintCount,
            "goodLetters": self.goodLetters,
            "badLetters": self.badLetters,
            "xp": self.xp,
            "xpmax": self.xpmax
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
        to_extract= cls(data["words"], data["lives"])
        to_extract.id= data["id"]
        to_extract.words= data["words"]
        to_extract.words2= data["words2"]
        to_extract.lives= data["lives"]
        to_extract.time= data["time"]
        to_extract.word= data["word"]
        to_extract.hintCount= data["hintCount"]
        to_extract.goodLetters= data["goodLetters"]
        to_extract.badLetters= data["badLetters"]
        to_extract.xp = data["xp"]
        to_extract.xpmax = data["xpmax"]


        return to_extract
    
    

@hangman_bp.route('/dashboard/games/hangman/<int:list_id>')
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
        if index == 0 and game["lesson_id"] == hangman_id:
            game = hangman(list_result["words"], 5)
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
def select_word():
    game = hangman.from_json(session["game"])
    result = game.new_word()
    session["game"] = game.to_json()
    return result

@hangman_bp.route('/dashboard/games/hangman/session/check_letter/<string:e>')
def check(e):
    game = hangman.from_json(session["game"])
    result = game.checking_letter(e)
    session["game"] = game.to_json()
    return result


@hangman_bp.route('/dashboard/games/hangman/session/reset')
def reset():
    game = hangman.from_json(session["game"])
    result = game.reset_letter()
    session["game"] = game.to_json()
    return result

@hangman_bp.route('/dashboard/games/hangman/session/askhint')
def new_hint():
    game = hangman.from_json(session["game"])
    result = game.ask_hint()
    session["game"] = game.to_json()
    return result