"""
This module contains the Hangman game.

Imports:
    - flask: For handling the requests and responses
    - flask_login: For managing the user sessions
    - root: For managing the database connection
    - random: For generating random numbers
    - datetime: For managing the date and time
    - uuid: For generating unique identifiers
    - json: For managing JSON data
    - functools: For managing the decorators
    - logging: For logging errors
    - time: For managing the time
    
Blueprints:
    - hangman_bp: The blueprint for the Hangman game
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

hangman_bp = Blueprint('hangman', __name__)
"""
The blueprint of the Hangman game.

Attributes:
    - hangman_bp: The blueprint of the Hangman game
    
Routes:
    - /dashboard/games/hangman/<int:list_id>: The route to initialize the game
    - /dashboard/games/hangman/<string:session_id>: The route to start the game
    - /dashboard/games/hangman/<string:session_id>/check_letter/<string:l>: The route to check a letter
    - /dashboard/games/hangman/<string:session_id>/askhint: The route to ask for a hint
    - /dashboard/games/hangman/<string:session_id>/check_status: The route to check the status of the game
"""

# The identifier of the Hangman game
hangman_id = 2

class hangman():
    """
    Represents the Hangman game.
    
    Attributes:
        - id (string): The unique identifier of the game
        - list_id (int): The id of the list
        - lesson_id (int): The id of the lesson
        - words (list): The words to check
        - words_to_check (list): The words to check
        - total_time (int): The total time of the game
        - time (string): The time when the game ends
        - start (string): The time when the game started
        - xpTotal (int): The total experience points
        - current_word (dict): The current word
        
    Methods:
        - new_word: Get a new word
        - checking_letter: Check a letter
        - ask_hint: Ask for a hint
        - get_remaning_time: Get the remaining time
        - get_words_checked: Get the words that have been checked
        - _lose_life: Lose a life
        - _end_game: End the game and save the results
        - to_json: Convert the list to JSON
        - from_json: Convert the JSON string to an object
    """
    def __init__(self, list_id, lesson_id, words):
        self.id = str(uuid.uuid4())
        self.list_id = list_id
        self.lesson_id = lesson_id
        self.words = words
        while len(self.words) > 6:
            self.words.pop(random.randint(0, len(words)-1))
        self.words_to_check = self.words.copy()
        self.total_time = len(words) * 20
        self.time = str(datetime.datetime.now() + datetime.timedelta(seconds=self.total_time))
        self.start = str(datetime.datetime.now())
        self.xpTotal = 0
        self.current_word = None

    def new_word(self, xp=0):
        """
        Get a new word
        
        Args:
            xp (int): The experience points gained
            
        Returns:
            dict: The response of the request
                - code (int): The status code of the request
                    -> 200: The request is successful
                - message (string): The message of the request
                - result (dict): The result of the request
                    -> bad (list): The bad letters
                    -> last_word (string): The last word
                    -> total_xp (int): The total experience points
                    -> xp_won (int): The experience points gained
                    -> len_word (int): The length of the word
                    -> spaces_positions (list): The positions of the spaces
                    -> correct (bool): The correctness of the last word
                    -> finished (bool): The finish status of the last word
            function: The _end_game function
        """
        # Check if there are still words to check
        if len(self.words_to_check) > 0:
            self.xpTotal += xp # Add the experience points
            word_choosen = random.choice(self.words_to_check) # Choose a new word
            
            # Check if the new word has an example
            is_example = word_choosen["examples"] 
            
            # Check if the last word is correct
            if self.current_word:
                is_last_word_correct = True if self.current_word["remaining_letters"] in [0, 1] else False
            else:
                is_last_word_correct = False
                
            # Get the bad letters and the last word
            bad_letters = self.current_word["bad_letter"] if self.current_word else []
            word = self.current_word["word"]["word"] if self.current_word else ""
            
            # Get the spaces positions of the new word
            spaces_positions = [i for i, l in enumerate(word_choosen["word"]) if l == " "]
            word_choosen["word"] = ''.join([i for i in word_choosen["word"] if i != " "]) # Remove the spaces   
            
            # Initialize the new word
            self.current_word = {
                "word": word_choosen,
                "nb_hints": 0,
                "max_hint": 3 if is_example else 2,
                "remaining_letters": len(word_choosen["word"]),
                "spaces_positions": spaces_positions,
                "good_letter": [],
                "bad_letter": [],
                "max_xp": 5
            }
            return jsonify({
                "code": 200,
                "message": "word_finished",
                "result": {
                    "bad": bad_letters,
                    "last_word": word,
                    "total_xp": self.xpTotal,
                    "xp_won": xp,
                    "len_word": len(word_choosen["word"]),
                    "spaces_positions": spaces_positions,
                    "correct": is_last_word_correct,
                    "finished": False if len(self.words_to_check) == len(self.words) else True
                }
            })
        else:
            return self._end_game(xp)

    def checking_letter(self, letter):
        """
        Check a letter
        
        Args:
            letter (string): The letter to check
            
        Returns:
            dict: The response of the request
                - code (int): The status code of the request
                    -> 200: The request is successful
                - message (string): The message of the request
                - result (dict): The result of the request
                    -> good (list): The good letters
                    -> bad (list): The bad letters
                    -> letter_position (list): The positions of the letter (If the letter is correct)
                    -> correct (bool): The correctness of the letter
                    -> finished (bool): The finish status of the word
        
        """
        # Check if the letter has already been touched
        all_letters = self.current_word["good_letter"] + self.current_word["bad_letter"]
        for i in all_letters:
            if i.lower() == letter.lower():
                return jsonify({
                    "code": 200,
                    "message": "already touch",
                    "result": []
                })
        
        # Check if the amount of bad letters is greater than 5 and if the letter to check is not in the word
        stop = True if len(self.current_word["bad_letter"]) == 5 and not letter in self.current_word["word"]["word"] else False
        if not letter.lower() in self.current_word["word"]["word"].lower():
            # Define the maximum experience points
            if len(self.current_word["bad_letter"]) < 2:
                self.current_word["max_xp"] = 5
            if len(self.current_word["bad_letter"]) >= 2 and len(self.current_word["bad_letter"]) < 4:
                self.current_word["max_xp"] = 3
            elif len(self.current_word["bad_letter"]) == 4:
                self.current_word["max_xp"] = 2
            elif len(self.current_word["bad_letter"]) == 5:
                self.current_word["max_xp"] = 1
            elif len(self.current_word["bad_letter"]) == 6:
                self.current_word["max_xp"] = 0
                
            # Add the letter to the bad letters
            self.current_word["bad_letter"].append(letter.lower())
            
            # If the letter is false and the amount of bad letters is greater than 5, the game is stopped
            if stop:
                pass
            else:
                return jsonify({
                    "code": 200,
                    "message": "wrong letter",
                    "result": {
                        "good": self.current_word["good_letter"],
                        "bad": self.current_word["bad_letter"],
                        "correct": False,
                        "finished": False
                    }
                })
                
        def next_step():
            """
            Go to the next step
            
            Returns:
                function: The new_word function
                function: The _end_game function
            """
            # Remove the word from the list of words to check
            for index, word_to_check in enumerate(self.words_to_check):
                if word_to_check["word"].lower() == self.current_word["word"]["word"].lower():
                    self.words_to_check.pop(index) # Remove
                    # If the list of words to check is empty, the game is ended
                    if len(self.words_to_check) == 0:
                        return self._end_game(self.current_word["max_xp"])
                    else:       
                        return self.new_word(self.current_word["max_xp"]) # Get a new word
                    
        if stop:
            # If the game is stopped, go to the next step
            return next_step()
        else:
            ### IF THE LETTER IS CORRECT ###
            # Add the letter to the good letters
            self.current_word["good_letter"].append(letter.lower())
            # Update the remaining letters
            self.current_word["remaining_letters"]-= sum([1 for i in self.current_word["word"]["word"] if i.lower() == letter.lower()])
            # If the word is finished, go to the next step
            if self.current_word["remaining_letters"] == 0:
                return next_step()
            # Get the positions of the letter to return to the javascript
            letter_position = [i for i, l in enumerate(self.current_word["word"]["word"]) if l.lower() == letter.lower()]
            return jsonify({
                "code": 200,
                "message": "correct letter",
                "result": {
                    "good": self.current_word["good_letter"],
                    "bad": self.current_word["bad_letter"],
                    "letter_position": letter_position,
                    "correct": True,
                    "finished": False
                }
            })

    def ask_hint(self):
        """
        Ask for a hint
        
        Returns:
            dict: The response of the request
                - code (int): The status code of the request
                    -> 200: The request is successful
                    -> 404: The request is not successful
                - message (string): The message of the request
                - result (dict): The result of the request
                    - title (string): The title of the hint
                    - hint (string): The hint of the word
        """
        # Update the number of hints
        hintCount = self.current_word["nb_hints"]
        # Check if the number of hints is less than the maximum number of hints
        if hintCount < self.current_word["max_hint"]:
            # Update the maximum experience points
            self.current_word["nb_hints"] += 1
            if hintCount == 0:
                self.current_word["max_xp"] = 4 if self.current_word["max_xp"] > 4 else self.current_word["max_xp"]
                return jsonify({
                    "code": 200,
                    "message": "hint",
                    "result": {
                        "title": "Type du mot",
                        "hint": self.current_word["word"]["type"]
                    }
                })
            elif hintCount == 1:
                self.current_word["max_xp"] = 3 if self.current_word["max_xp"] > 3 else self.current_word["max_xp"]
                if self.current_word["word"]["examples"]:
                    return jsonify({
                        "code": 200,
                        "message": "hint",
                        "result": {
                            "title": "Un example en français",
                            "hint": self.current_word["word"]["trans_examples"][0]
                        }
                    })
                else:
                    return jsonify({
                        "code": 200,
                        "message": "hint",
                        "result": {
                            "title": "Le mot en français",
                            "hint": self.current_word["word"]["trans_word"]
                        }
                    })
            else:
                self.current_word["max_xp"] = 2 if self.current_word["max_xp"] > 2 else self.current_word["max_xp"]
                return jsonify({
                    "code": 200,
                    "message": "hint",
                    "result": {
                        "title": "Le mot en français",
                        "hint": self.current_word["word"]["trans_word"]
                    }
                })
        else:
            return jsonify({
                "code": 404,
                "message": "no hint",
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
                pass

        except Exception as e:
            logging.error("An error has occured: " + str(e))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                
    def _end_game(self, xp=0):
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
            xp = self.xpTotal + xp
            
            lives_to_lose = 1 if (xp/(len(self.words)*5)) < 0.80 else 0
            lives_lost = lives_to_lose
            while lives_to_lose > 0:
                self._lose_life()
                lives_to_lose -= 1
            
            # Check if the lesson has already been played
            cursor.execute("SELECT * FROM lessons_log WHERE user_id = %s AND lesson_id = %s", (current_user.id, self.lesson_id))
            is_already_completed = cursor.fetchall()
            if is_already_completed:
                xp = round(xp  * 0.66) # Reduce the experience points by 33%
                
            # Update the lesson as completed
            if lives_lost == 0:
                cursor.execute("UPDATE lessons SET completed = 1 WHERE id = %s", (self.lesson_id,))
                        
            # Save the results in the database
            cursor.execute("INSERT INTO lessons_log (user_id, list_id, lesson_id, xp, lost_lives, time) VALUES (%s, %s, %s, %s, %s, %s)", (current_user.id, self.list_id, self.lesson_id, xp, lives_lost, time_passed))
            cursor.execute("INSERT INTO user_statements SET user_id= %s, transaction_type = 'xp', transaction = %s", ( current_user.id, xp))
            conn.commit()
            
            response = jsonify({
                "code": 201,
                "message": "Le jeu est terminé!",
                "result": {
                    "time": time_passed,
                    "xp": xp,
                    "lost_lives": lives_lost
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
        Convert the list to JSON.

        Returns:
            dict: The list in JSON.
        """
        return json.dumps(self, default=lambda o: o.__dict__) 

        
    @classmethod
    def from_json(cls, json_string):
        """
        Create a list from JSON.

        Args:
            json_data (dict): The list in JSON.

        Returns:
            WordList: The list.
        """
        json_dict = json.loads(json_string)
        to_extract = cls(json_dict["list_id"], json_dict["lesson_id"], json_dict["words"])
        to_extract.id = json_dict["id"]
        to_extract.total_time = json_dict["total_time"]
        to_extract.time = json_dict["time"]
        to_extract.words_to_check = json_dict["words_to_check"]
        to_extract.start = json_dict["start"]
        to_extract.xpTotal = json_dict["xpTotal"]
        to_extract.current_word = json_dict["current_word"]

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
            game = hangman.from_json(session["game"])
            # Check if the game is still in progress
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
    # Return the wrapper function
    return wrapper_function

@hangman_bp.route('/dashboard/games/hangman/<int:list_id>')
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
        if index == 0 and game["lesson_id"] == hangman_id:
            game = hangman(list_result["id"], game["id"], list_result["words"])
            id = game.id
            session['game'] = game.to_json()
            return redirect(url_for('hangman.start', session_id=id))
        elif index > 0 and list_result["lessons"][index-1]["completed"] == 1 and game["lesson_id"] == hangman_id:
            game = hangman(list_result["id"], game["id"], list_result["words"])
            id = game.id
            session['game'] = game.to_json()
            return redirect(url_for('hangman.start', session_id=id))
    
    # If the game is not available, return a 404 error
    abort(404)
    
@hangman_bp.route('/dashboard/games/hangman/<string:session_id>')
def start(session_id):
    """
    Start the game by displaying the game interface
    
    Args:
        session_id (string): The unique identifier of the game
        
    Returns:
        flask.redirect: 
    """
    if 'game' in session:
        game = hangman.from_json(session["game"])
        if not game.current_word:
            game.new_word()
        
        reloaded = True if game.get_remaning_time() < (game.total_time - 2) else False
        if session_id == game.id and game.time > str(datetime.datetime.now()):
            session["game"] = game.to_json()
            return render_template('games/hangman.html', 
                                   session_id=session_id, 
                                   list_id=game.list_id,
                                   time=game.get_remaning_time(),
                                   len_word=len(game.current_word["word"]["word"]),
                                   letters_used=game.current_word["good_letter"] + game.current_word["bad_letter"],
                                   bad_letters=game.current_word["bad_letter"],
                                   good_letters=game.current_word["good_letter"],
                                   word=game.current_word["word"]["word"],
                                   space_positions=game.current_word["spaces_positions"],
                                   score=game.xpTotal,
                                   reloaded=reloaded)
        return redirect(url_for('hangman.index', list_id=game.list_id))
    return redirect(url_for('main.index'))

@hangman_bp.route('/dashboard/games/hangman/<string:session_id>/check_letter/<string:l>')
@check_game
def check(session_id, l):
    game = hangman.from_json(session["game"])
    result = game.checking_letter(l)
    session["game"] = game.to_json()
    time.sleep(1/100)
    
    # Check if the game is ended
    if result.status_code == 201:
        session.pop('game', None) # Remove the game from the session
    return result

@hangman_bp.route('/dashboard/games/hangman/<string:session_id>/askhint')
def new_hint(session_id):
    
    game = hangman.from_json(session["game"])
    result = game.ask_hint()
    session["game"] = game.to_json()
    time.sleep(1/100) 
    
    # Check if the game is ended
    if result.status_code == 201:
        session.pop('game', None) # Remove the game from the session
    return result

@hangman_bp.route('/dashboard/games/hangman/<string:session_id>/check_status')
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
    game = hangman.from_json(session["game"])
    return jsonify({
        "code": 200,
        "message": "Le jeu est en cours!",
        "result": {}
    })