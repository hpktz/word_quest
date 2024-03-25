"""
This module contains the routes for the typefast game.

Imports:
    - flask: For handling the requests and responses
    - flask_login: For handling the user sessions
    - root: For the connection to the database
    - random: For generating random numbers
    - datetime: For handling the dates and times
    - uuid: For generating unique identifiers
    - json: For handling the JSON data
    - functools: For handling the decorators
    - logging: For logging the errors
    - time: For handling the time

Blueprints:
    - typefast_bp: The blueprint for the typefast game 

"""

from flask import Blueprint, render_template, redirect, url_for, jsonify, request, session, abort, make_response
from flask_login import login_user, login_required, logout_user, current_user
from root import *
import random as random
import datetime as datetime
import uuid as uuid
import json
from functools import wraps 
import logging
import time

typefast_bp = Blueprint('typefast', __name__)
"""
The blueprint for the typefast game

Attributes:
    -typefast_bp: The blueprint for the typefast game
    
Routes: 
    - /dashboard/games/typefast/<int:list_id>: The route to initialize the game
    - /dashboard/games/typefast/<string:session_id>: The route to start the game by displaying the game interface
    - /dashboard/games/typefast/<string:session_id>/check_word/<string:word>: The route to check if the word is correct
    - /dashboard/games/typefast/<string:session_id>/check_status: The route to check the status of the game
"""

# The id of the typefast game
typefast_id = 7

class typeFast():
    """
    Reprents the typefast game
    
    Attributes:
        - id (string): The unique identifier of the game
        - list_id (int): The id of the list
        - lesson_id (int): The id of the lesson
        - words (list): The words to check
        - words_to_check (list): The words to check
        - time (string): The time when the game will end
        - start (string): The time when the game started
        
    Methods:
        - check_word: Check if the word is correct
        - get_remaning_time: Get the remaining time
        - get_words_checked: Get the words that have been checked
        - _lose_life: Lose a life
        - _end_game: End the game
        - to_json: Convert the object to a JSON string
        - from_json: Convert the JSON string to an object
    """
    def __init__(self, list_id, lesson_id, words):
        self.id = str(uuid.uuid4())
        self.list_id = list_id
        self.lesson_id = lesson_id
        self.words = words
        self.words_to_check = words
        self.time = str(datetime.datetime.now() + datetime.timedelta(minutes=2))
        self.start = str(datetime.datetime.now())
        
    def check_word(self, word):
        """
        Check if the word is correct

        Args:
            word (string): The word to check

        Returns:
            dict: The response of the request if the game is still in progress
                - code (int): The status code of the request
                    -> 200: The word is correct
                    -> 404: The word is incorrect
                - message (string): The message of the request
                - result (dict): The result of the request
                    - remaining (int): The number of remaining words
                    - time (string): The time when the game started
                    - xp (int): The experience points gained
                    - lost_lives (int): The number of lost lives
            function: The _end_game function if the game is ended
        """
        if self.time < str(datetime.datetime.now()) or len(self.words_to_check) == 0:
            return self._end_game()
        
        for index, word_to_check in enumerate(self.words_to_check):
            if word_to_check["word"].strip() == word.strip():
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
        
    def _end_game(self):
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
            time_passed = time_passed.total_seconds()
            xp = round((((len(self.words)-len(self.words_to_check)) * 5) / time_passed)*10)
                
            # Lose a life if there are remaining words
            lives_to_lose = 1 if len(self.words_to_check) > 0 else 0
            while lives_to_lose > 0:
                self._lose_life()
                lives_to_lose -= 1
            
            lives_to_lose = 1 if len(self.words_to_check) > 0 else 0
            
            is_already_completed = cursor.execute("SELECT * FROM lessons_log WHERE user_id = %s AND lesson_id = %s", (current_user.id, self.lesson_id))
            is_already_completed = cursor.fetchall()
            if is_already_completed:
                xp = round(xp  * 0.66)
            else:
                if lives_to_lose == 0:
                    session["path_finished"] = True
                    cursor.execute("INSERT INTO user_statements SET user_id= %s, transaction_type = 'gems', transaction = %s", (current_user.id, 200))
                
            # Update the lesson as completed
            if lives_to_lose == 0:
                cursor.execute("UPDATE lessons SET completed = 1 WHERE id = %s", (self.lesson_id,))
            
            # Save the results in the database
            cursor.execute("INSERT INTO lessons_log (user_id, list_id, lesson_id, xp, lost_lives, time) VALUES (%s, %s, %s, %s, %s, %s)", (current_user.id, self.list_id, self.lesson_id, xp, lives_to_lose, time_passed))
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
        to_extract.time = json_dict["time"]
        to_extract.words_to_check = json_dict["words_to_check"]
        to_extract.start = json_dict["start"]
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
            game = typeFast.from_json(session["game"])
            # Check if the game is still in progress
            if session_id != game.id or game.time < str(datetime.datetime.now()):
                response = game._end_game()
                session["game"] = game.to_json()
                if response.status_code == 201:
                    session.pop('game', None)
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

@typefast_bp.route('/dashboard/games/typefast/<int:list_id>')
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
    
    # If the game is not available, return a 404 error
    abort(404)
    

@typefast_bp.route('/dashboard/games/typefast/<string:session_id>')
def start(session_id):
    """
    Start the game by displaying the game interface
    
    Args:
        session_id (string): The unique identifier of the game
        
    Returns:
        flask.redirect: 
    """
    if 'game' in session:
        game = typeFast.from_json(session["game"])
        reloaded = True if game.get_remaning_time() < 118 else False
        if session_id == game.id and game.time > str(datetime.datetime.now()):
            return render_template('games/typefast.html', 
                                   session_id=session_id, 
                                   list_id=game.list_id, 
                                   score=len(game.words_to_check), 
                                   max_score=len(game.words), 
                                   time=game.get_remaning_time(),
                                   words=game.get_words_checked(),
                                   reloaded=reloaded)
        return redirect(url_for('typefast.index', list_id=game.list_id))
    return redirect(url_for('main.index'))
    
@typefast_bp.route('/dashboard/games/typefast/<string:session_id>/check_word/<string:word>')
@check_game
def check_word(session_id, word):
    """
    Check if the word is correct
    
    Args:
        session_id (string): The unique identifier of the game
        word (string): The word to check
    
    Returns:
        flask.Response: The response of the request
    """
    game = typeFast.from_json(session["game"])
    response = game.check_word(word)
    session["game"] = game.to_json()
    time.sleep(1/100)

    if response.status_code == 201:
        session.pop("game", None)

    return response

@typefast_bp.route('/dashboard/games/typefast/<string:session_id>/check_status')
@check_game
def check_status(session_id):
    """
    Check the status of the game
    
    Args:
        session_id (string): The unique identifier of the game
    
    Returns:
        dict: The response of the request
            - code (int): The status code of the request
                -> 200: The game is in progress
            - message (string): The message of the request
            - result (dict): The result of the request
                - remaining (int): The number of remaining words
                - time (string): The time when the game started
                - words (list): The words that have been checked
    """
    game = typeFast.from_json(session["game"])
    return jsonify({
        "code": 200,
        "message": "Le jeu est en cours!",
        "result": {
            "remaining": len(game.words_to_check),
            "time": game.get_remaning_time(),
            "words": game.get_words_checked()
        }
    })