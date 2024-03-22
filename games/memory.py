"""
This module contains the routes and functions to manage the quiz game

Imports:
    - flask: For handling the requests and responses
    - flask_login: For managing the user sessions
    - root: For managing the database connection
    - random: For generating random numbers
    - datetime: For managing the date and time
    - uuid: For generating unique identifiers
    - json: For managing JSON data
    - functools: For managing the decorators
    - Levenshtein: For calculating the Levenshtein distance
    - GoogleImagesSearch: For searching images on Google
    - gTTS: For generating audio from text
    - BytesIO: For managing the audio bytes
    - logging: For logging errors
    
Blueprints:
    - quiz_bp: The blueprint of the quiz game
"""

from flask import Blueprint, render_template, redirect, url_for, jsonify, request, session, abort, make_response, Response
from flask_login import login_user, login_required, logout_user, current_user
from root import *
import random as random
import datetime as datetime
import uuid as uuid
import json
from functools import wraps
import time

import logging


memory_bp = Blueprint('memory', __name__)
"""
The blueprint of the quiz game

Attributes:
    -quiz_bp: The blueprint of the quiz game

Routes:
    - /dashboard/games/quiz/<int:list_id>: Initialize the game and redirect to the game interface
    - /dashboard/games/quiz/<string:session_id>: Start the game by displaying the game interface
    - /dashboard/games/memory/<int:list_id>/getCard: Get the cards of the game
    - /dashboard/games/quiz/<string:session_id>/check/<int:answer>: Check the answer of the game
    - /dashboard/games/quiz/<string:session_id>/check_status: Check if the game is still in progress
"""

# The id of the quiz lesson
memory_id = 4

class memory():
    """
    Represents a quiz game
    
    Attributes:
        - id (string): The unique identifier of the game
        - list_id (int): The id of the list
        - lesson_id (int): The id of the lesson
        - words (list): The words of the lesson
        - words_to_check (list): The words to check
        - time (string): The time when the game ends
        - start (string): The time when the game started
        - current_quiz (dict): The current question
        - faults (int): The number of faults
        
    Methods:
        - check_answer: Check the answer of the user
        - ask_next_question: Ask the next question
        - get_remaning_time: Get the remaining time
        - get_words_checked: Get the words that have been checked
        - _lose_life: Lose a life
        - _end_game: End the game and save the results
        - to_json: Convert the object to a JSON string
        - from_json: Convert the JSON string to an object
    """
    def __init__(self, list_id, lesson_id, words):
        self.id = str(uuid.uuid4())
        self.list_id = list_id
        self.lesson_id = lesson_id
        self.words = words
        while len(self.words) > 7:
            self.words.pop(random.randint(0, len(words)-1))
        self.words_to_check = words
        self.time = str(datetime.datetime.now() + datetime.timedelta(minutes=1))
        self.start = str(datetime.datetime.now())
        self.french_words = [[word['trans_word'], str(i), "french"] for i, word in enumerate(self.words)]
        self.english_words = [[word['word'], str(i), "english"] for i, word in enumerate(self.words)]
        self.cards = self.french_words + self.english_words
        self.shuffle_cards = []
        self.open_cards = []
        self.nbr_try = 0

    def getWords(self):
        liste = []
        for i in range(len(self.cards)):
            current_card = random.choice(self.cards)
            self.shuffle_cards.append(current_card)
            self.cards.remove(current_card)
        return jsonify({
            'code': 200,
            'message': 'ok',
            'result': {'nbr_cards': len(self.french_words + self.english_words)}
        })
        
    def printWord(self, id):
        el = self.shuffle_cards[id]
        checking = self.checking_cards(el)
        if(len(self.cards) == len(self.shuffle_cards)):
            return self._end_game(checking, id)
        return jsonify({
            'code': 200,
            'message': 'ok',
            'result': { 'innerHTML': self.shuffle_cards[id][0],
                       'checking': checking}
        })
    
    def checking_cards(self, new_card):
        self.open_cards.append(new_card)
        if len(self.open_cards) == 2:
            self.nbr_try += 1
            if self.open_cards[0][1] == self.open_cards[1][1]:
                self.cards.append(self.open_cards[0])
                self.cards.append(self.open_cards[1])
                self.open_cards = []
                return True
            else:
                self.open_cards = []
                return False
        return None

    # Creer un attribut "carte en cours" qui stock les cartes que l'utilisateur vient de clicker
    # si l'attribut a une longueur de 1, on attend
    # si il a une longueur de 2, on compare les 2 et on regarde si c'est juste


    def get_remaning_time(self):
        """
        Get the remaining time
        
        Returns:
            int: The remaining time in seconds
        """
        return round((datetime.datetime.strptime(self.time, '%Y-%m-%d %H:%M:%S.%f') - datetime.datetime.now()).total_seconds())
       
    def get_words_checked(self):
        """
        Get the words that have been checked
        
        Returns:
            list: The words that have been checked
        """
        words = []
        for word in self.words:
            if word not in self.words_to_check:
                words.append(word)
        return words
    
    def _lose_life(self):
        """
        Lose a life
        
        Returns:
            None
            
        Raises:
            Exception: An error has occured
        """
        conn = None
        cursor = None
        try:
            conn = create_connection()
            cursor = conn.cursor()
            if current_user.get_lives() > 0:
                cursor.execute("INSERT INTO user_statements (user_id, transaction_type, transaction) VALUES (%s, 'lives', -1);", (current_user.id,))
                conn.commit()

        except Exception as e:
            logging.error("An error has occured: " + str(e))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        
    def _end_game(self, last_answer, last_id):
        """
        End the game and save the results
        
        Returns:
            dict: The response of the request
                - code (int): The status code of the request
                    -> 201: The game is ended
                    -> 500: An error has occured
                - message (string): The message of the request
                - result (dict): The result of the request
                    - remaining (int): The number of remaining words
                    - time (string): The time when the game started
                    - xp (int): The experience points gained
                    - lost_lives (int): The number of lost lives 
        Raises:
            Exception: An error has occured
        """
        conn = None
        cursor = None
        try:
            conn = create_connection()  
            cursor = conn.cursor()
            
            # Calculate the experience points
            time_passed = datetime.datetime.now() - datetime.datetime.strptime(self.start, '%Y-%m-%d %H:%M:%S.%f')
            time_passed = round(time_passed.total_seconds())

            if last_id == None:
                xp = 0
            elif self.nbr_try > len(self.french_words)*1.5:
                xp = 20 - round(self.nbr_try - len(self.french_words)*1.5)
                xp = xp if xp > 0 else 0
            else:
                xp = 20
                
            # Lose a life if there are remaining words
            lives_to_lose = 1 if xp < 15 else 0
            while lives_to_lose > 0:
                self._lose_life()
                lives_to_lose -= 1
            
            lives_to_lose = 1 if xp < 15 else 0

            is_already_completed = cursor.execute("SELECT * FROM lessons_log WHERE user_id = %s AND lesson_id = %s", (current_user.id, self.lesson_id))
            is_already_completed = cursor.fetchall()
            if is_already_completed:
                xp = xp//2

            # Update the lesson as completed
            if lives_to_lose == 0:
                cursor.execute("UPDATE lessons SET completed = 1 WHERE id = %s", (self.lesson_id,))
                        
            # Save the results in the database
            cursor.execute("INSERT INTO lessons_log (user_id, list_id, lesson_id, xp, lost_lives, time) VALUES (%s, %s, %s, %s, %s, %s)", (current_user.id, self.list_id, self.lesson_id, xp, lives_to_lose, time_passed))
            cursor.execute("INSERT INTO user_statements SET user_id= %s, transaction_type = 'xp', transaction = %s", ( current_user.id, xp))
            conn.commit()
            if last_id == None:
                response = jsonify({
                "code": 201,
                "message": "Le jeu est terminé!",
                "result": {
                    "time": time_passed,
                    "lost_lives": lives_to_lose,
                    "xp": xp,
                    "score": len(self.cards)//2,
                    "total": len(self.words)
                }
            })
            else:
                response = jsonify({
                    "code": 201,
                    "message": "Le jeu est terminé!",
                    "result": {
                        "remaining": len(self.words_to_check),
                        "time": time_passed,
                        "lost_lives": lives_to_lose,
                        "xp": xp,
                        'innerHTML': self.shuffle_cards[last_id][0],
                        'checking': last_answer,
                        "score": len(self.cards)//2,
                        "total": len(self.words)
                    }
                })
            response = make_response(response, 201)
            return response
        except Exception as e:
            logging.error("An error has occured: " + str(e))
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
        """ 
        Convert the object to a JSON string
        
        Returns:
            string: The JSON string of the object
        """
        return json.dumps(self, default=lambda o: o.__dict__) 

    # Class method to create an object from a JSON string
    @classmethod
    def from_json(cls, json_string):
        """ 
        Convert the JSON string to an object
        
        Args:
            json_string (string): The JSON string to convert
        
        Returns:
            object: The object extracted from the JSON string
        """
        json_dict = json.loads(json_string)
        to_extract = cls(json_dict["list_id"], json_dict["lesson_id"], json_dict["words"])
        to_extract.id = json_dict["id"]
        to_extract.words_to_check = json_dict["words_to_check"]
        to_extract.time = json_dict["time"]
        to_extract.start = json_dict["start"]
        to_extract.cards = json_dict["cards"]
        to_extract.shuffle_cards = json_dict["shuffle_cards"]
        to_extract.open_cards = json_dict["open_cards"]
        to_extract.nbr_try = json_dict["nbr_try"]
        return to_extract    


# Decorator to check if the game is still in progress
def check_game(func):
    @wraps(func)
    def wrapper_function(session_id, *args, **kwargs):
        """
        Check if the game is still in progress
        
        Args:
            session_id (string): The unique identifier of the game
            *args: The arguments of the function
            **kwargs: The keyword arguments of the function
        
        Returns:
            dict: The response of the request
                - code (int): The status code of the request
                    -> 404: The game is not found
                - message (string): The message of the request
                - result (list): The result of the request
            function: The function to execute
        """
        if 'game' in session:
            game = memory.from_json(session["game"])
            # Check if the game is still in progress
            if session_id != game.id or game.time < str(datetime.datetime.now()):
                response = game._end_game(None,None)
                session["game"] = game.to_json()
                session.pop("game", None)

                return response
            else:
                return func(session_id, *args, **kwargs)
        return jsonify({
            "code": 404,
            "message": "Le jeu n'a pas été trouvé!",
            "result": []
        })
    # Return the wrapper function
    return wrapper_function

@memory_bp.route('/dashboard/games/memory/<int:list_id>')
@login_required
def index(list_id):
    """ 
    Inialize the game and redirect to the game interface
    
    Args:
        list_id (int): The id of the list
        
    Returns:
        function: The redirect function
        abort: Return a 404 error
    """
    
    # Check if the user has lives
    if current_user.get_lives() == 0:
        return redirect(url_for('main.index', hearts_message=True))
    
    # Check if the list exists
    list_result = [l for l in current_user.get_lists() if l["id"] == list_id]
    if not list_result:
        abort(404)
    else:
        list_result = list_result[0]
    
    # Sort the lessons by order    
    list_result["lessons"] = sorted(list_result["lessons"], key=lambda k: k['odr'])

    # Check if the game exists and if it is available
    for index, game in enumerate(list_result["lessons"]):
        if index == 0 and game["lesson_id"] == memory_id:
            game = memory(list_result["id"], game["id"], list_result["words"])
            id = game.id
            session['game'] = game.to_json()
            return redirect(url_for('memory.start', session_id=id))
        elif index > 0 and list_result["lessons"][index-1]["completed"] == 1 and game["lesson_id"] == memory_id:
            game = memory(list_result["id"], game["id"], list_result["words"])
            id = game.id
            session['game'] = game.to_json()
            return redirect(url_for('memory.start', session_id=id))
    
    # If the game is not available, return a 404 error
    abort(404)
@memory_bp.route('/dashboard/games/memory/<string:session_id>')
def start(session_id):
    """
    Start the game by displaying the game interface
    
    Args:
        session_id (string): The unique identifier of the game
        
    Returns:
        flask.redirect: 
    """
    if 'game' in session:
        game = memory.from_json(session["game"])
        if not game.shuffle_cards:
            game.getWords()
        else:
            return redirect(url_for('memory.index', list_id=game.list_id))
        
        shuffle_cards = game.shuffle_cards
        cards = game.cards
        reloaded = True if game.get_remaning_time() < 58 else False
        if session_id == game.id and game.time > str(datetime.datetime.now()):
            session["game"] = game.to_json()
            return render_template('games/memory.html', 
                                   session_id=session_id, 
                                   list_id=game.list_id,
                                   time=game.get_remaning_time(),
                                   shuffle_cards=shuffle_cards,
                                   cards=cards,
                                   reloaded=reloaded)
        return redirect(url_for('memory.index', list_id=game.list_id))
    return redirect(url_for('main.index'))

@memory_bp.route('/dashboard/games/memory/<string:session_id>/check_status')
@check_game
def check_status(session_id):
    """
    Check if the game is still in progress
    
    Args:
        session_id (string): The unique identifier of the game
    
    Returns:
        dict: The response of the request
            - code (int): The status code of the request
                -> 200: The request is successful
            - message (string): The message of the request
            - result (dict): The result of the request
    """
    game = memory.from_json(session["game"])
    return jsonify({
        "code": 200,
        "message": "Le jeu est en cours!",
        "result": {}
    })

@memory_bp.route('/dashboard/games/memory/<string:session_id>/check_word/<int:boxId>')
@check_game
def test(session_id, boxId):
    game = memory.from_json(session["game"])
    result = game.printWord(boxId)
    session["game"] = game.to_json()
    time.sleep(1/100)
    
    if result.status_code == 201:
        session.pop("game", None)
    return result