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
    - gTTS: For generating audio from text
    - BytesIO: For managing the audio bytes
    - logging: For logging errors
    - time: For managing the time
    
Blueprints:
    - memowordrize_bp: The blueprint of the memowordrize game
"""

from flask import Blueprint, render_template, redirect, url_for, jsonify, request, session, abort, make_response, Response
from flask_login import login_user, login_required, logout_user, current_user
from root import *
import random as random
import datetime as datetime
import uuid as uuid
import json
from functools import wraps
from gtts import gTTS
from io import BytesIO
import logging
import time

memowordrize_bp = Blueprint('memowordrize', __name__)
"""
The blueprint of the memowordrize game

Routes:
    - /dashboard/games/memowordrize/<int:list_id>: The route to initialize the game
    - /dashboard/games/memowordrize/<string:session_id>: The route to start the game and display the game interface
    - /dashboard/games/memowordrize/<string:session_id>/see_path: The route to send the path of the game to the js interface
    - /dashboard/games/memowordrize/<string:session_id>/audio/<string:id>: The route to generate the audio of a word
    - /dashboard/games/memowordrize/<string:session_id>/try_case: The route to try a case in the game
    - /dashboard/games/memowordrize/<string:session_id>/check_status: The route to check the status of the game
    
Attributes:
    - memowordrize_id (int): The id of the quiz lesson
"""

# The id of the quiz lesson
memowordrize_id = 6

class memowordrize():
    """
    Represents a memowordrize game
    
    Attributes:
        - id (string): The unique identifier of the game
        - list_id (int): The id of the list
        - lesson_id (int): The id of the lesson
        - words (list): The words in the list
        - words_to_check (list): The words to check
        - time (string): The time when the game ends
        - start (string): The time when the game started
        - current_path (dict): The current path of the game
        - xp (int): The experience points gained
        - faults (int): The number of faults
        - game_count (int): The number of games played
    
    Methods:
        - see_path: Generate the current path
        - next_path: Generate the next path
        - check_case: Try a case
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
        self.words_to_check = words
        self.time = str(datetime.datetime.now() + datetime.timedelta(minutes=5))
        self.start = str(datetime.datetime.now())
        self.current_path = None
        self.xp = 0
        self.faults = 0
        self.game_count = 0
        
    def see_path(self):
        """
        Return the current path
        
        Returns:
            dict: The response of the request
                - code (int): The status code of the request
                    -> 200: The current path is accessible
                    -> 403: The current path has been seen too many times
                - message (string): The message of the request
                - result (dict): The result of the request
                    - tries (int): The number of tries
                    - path (list): The path of the game
                    - words (list): The shuffled words to place in the path
                    
            function: The next path function
                -> If no path has been generated, generate the next path (For the beginning of the game)
        """
        if self.current_path: # If the current path exists
            if self.current_path["tries"] < 3: # If the current path has been seen less than 3 times
                self.current_path["tries"] += 1 # Increment the number of tries
                # Get the words to place in the path
                words = [{key: value for key, value in item.items() if key in ["word"]} for item in self.current_path["path"]]
                words = [item["word"]["word"] for item in words] # Get the unique words
                words = random.sample(words, len(words)) # Shuffle the words
                return jsonify({
                    "code": 200,
                    "message": "Voici le chemin!",
                    "result": {
                        "tries": self.current_path["tries"],
                        "path": [{key: value for key, value in item.items() if key in ["id", "line", "position", "checked"]} for item in self.current_path["path"]],
                        "words": words
                    }
                })
            else:
                return jsonify({
                    "code": 403,
                    "message": "Chemin vu trop de fois!",
                    "result": []
                })
        return self.next_path()
        
    def next_path(self):
        """
        Generate the next path
        
        Returns:
            dict: The response of the request
                - code (int): The status code of the request
                    -> 200: The game is ready
                    -> 500: An error has occured
                - message (string): The message of the request
                - result (dict): The result of the request
                    - finished (bool): The game is finished
                    - xp (int): The experience points gained
                    - tries (int): The number of tries
                    - path (list): The path of the game
                    - words (list): The shuffled words to place in the path
        """
        try:
            if self.game_count > 3: # If the player has played more than 3 games
                return self._end_game()
            # Select the position of the first case
            starting_position = random.randint(1, 5)
            positions = [starting_position]
            self.game_count += 1
            for i in range(1, 6):
                # Add the next position
                next_positions = [positions[-1]]
                # 3 possibilities: go to the right, go to the left, stay at the same position
                # If the position is at the edge, the player can only go to the opposite direction
                next_positions.append(positions[-1] + 1 if positions[-1] < 5 else 5)
                next_positions.append(positions[-1] - 1 if positions[-1] > 1 else 1)
                positions.append(random.choice(next_positions)) # Add the next position
                
            path = [] # The path of the game
            for index, position in enumerate(positions):
                # Select a random word to place in the path
                word_choice = random.choice(self.words_to_check)
                dict_position = {
                    "id": str(uuid.uuid4()),
                    "line": index + 1,
                    "position": position + index * 5, # Calculate the position of the case in html
                    "word": word_choice,
                    "checked": False
                }
                path.append(dict_position) # Add the word to the path
                
                ### We do not remove the word from the word_to_check list
                ### Because if the player's list is to short, the game will be stuck
                ### The difficulty is a bit lower, but it do not affect the game
                
            self.current_path = {
                "tries": 0, # Set the number of tries to 0
                "path": path
            }
            # Calculate the experience points
            xp_won = 5 - self.faults * 0.3 if 5 - self.faults * 0.3 > 0 else 0
            self.xp += round(xp_won, 2)
            
            # Get the words to place in the path
            words = [{key: value for key, value in item.items() if key in ["word"]} for item in path]
            words = [item["word"]["word"] for item in words]
            words = random.sample(words, len(words)) # Shuffle the words
            
            return jsonify({
                "code": 200,
                "message": "Le jeu est prêt!",
                "result": {
                    "finished": True, # Indicate if the last path is finished
                    "xp": round(xp_won), # Xp won at the last game
                    "tries": 0,
                    "path": [{key: value for key, value in item.items() if key in ["id", "line", "position", "checked"]} for item in path],
                    "words": words
                }})
        except Exception as e:
            logging.error("An error has occured: " + str(e))
            return jsonify({
                "code": 500,
                "message": "Une erreur s'est produite!",
                "result": []
            }), 500
        
    def check_case(self, position, word):
        """
        Try a case
        
        Args:
            position (int): The position of the case
            word (string): The word to check
        
        Returns:
            dict: The response of the request
                - code (int): The status code of the request
                    -> 200: The game is ready
                    -> 500: An error has occured
                - message (string): The message of the request
                - result (dict): The result of the request
                    - tries (int): The number of tries
                    - path (list): The path of the game
        """
        if self.current_path: # If the current path exists
            # Check if the position exists in the path and it is correct
            check_position = None
            for index, el in enumerate(self.current_path["path"]):
                if el["position"] == int(position):
                    check_position = index
                    break
            # If the position is correct
            if check_position is not None:
                # Check if the word is correct
                if self.current_path["path"][check_position]["word"]["word"].lower() == word.lower():
                    self.current_path["path"][check_position]["checked"] = True # Set the case as checked
                    if all([item["checked"] for item in self.current_path["path"]]): # If all the cases are checked
                        return self.next_path() # Generate the next path
                    else:
                        return jsonify({
                            "code": 200,
                            "message": "Le mot est correct!",
                            "result": {
                                "finished": False,
                                "tries": self.current_path["tries"]
                            }
                        })
                else:
                    # If the word is incorrect
                    self.faults += 1
                    # Get the words to place in the path
                    words = [{key: value for key, value in item.items() if key in ["word"]} for item in self.current_path["path"]]
                    words = [item["word"]["word"] for item in words]
                    words = random.sample(words, len(words)) # Shuffle the words
                    for path in self.current_path["path"]:
                        path["checked"] = False # Set all the cases as unchecked
                    return jsonify({
                        "code": 403,
                        "message": "Le mot est incorrect!",
                        "result": {
                            "tries": self.current_path["tries"],
                            "words": words
                        }
                    })
            else:
                # If the position is incorrect
                self.faults += 1
                # Get the words to place in the path
                words = [{key: value for key, value in item.items() if key in ["word"]} for item in self.current_path["path"]]
                words = [item["word"]["word"] for item in words]
                words = random.sample(words, len(words)) # Shuffle the words
                for path in self.current_path["path"]:
                    path["checked"] = False # Set all the cases as unchecked
                return jsonify({
                    "code": 403,
                    "message": "Le mot est incorrect!",
                    "result": {
                        "tries": self.current_path["tries"],
                        "words": words
                    }
                })
        return jsonify({
            "code": 404,
            "message": "Le chemin n'a pas été trouvé!",
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
            time_passed = round(time_passed.total_seconds())
            xp = self.xp
                
            # Lose a life if there are remaining words
            lives_to_lose = 1 if xp < 15 else 0
            while lives_to_lose > 0:
                self._lose_life()
                lives_to_lose -= 1
            lives_to_lose = 1 if xp < 15 else 0
            
            # Check if the lesson has already been played
            cursor.execute("SELECT * FROM lessons_log WHERE user_id = %s AND lesson_id = %s", (current_user.id, self.lesson_id))
            is_already_completed = cursor.fetchall()
            if is_already_completed:
                xp = round(xp  * 0.66)
            
            if lives_to_lose == 0:    
                # Update the lesson as completed
                cursor.execute("UPDATE lessons SET completed = 1 WHERE id = %s", (self.lesson_id,))

            # Save the results in the database
            cursor.execute("INSERT INTO lessons_log (user_id, list_id, lesson_id, xp, lost_lives, time) VALUES (%s, %s, %s, %s, %s, %s)", (current_user.id, self.list_id, self.lesson_id, xp, lives_to_lose, time_passed))
            cursor.execute("INSERT INTO user_statements SET user_id= %s, transaction_type = 'xp', transaction = %s", ( current_user.id, xp))
            conn.commit()
            
            response = jsonify({
                "code": 201,
                "message": "Le jeu est terminé!",
                "result": {
                    "time": time_passed,
                    "xp": xp,
                    "lost_lives": lives_to_lose
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
        to_extract.current_path = json_dict["current_path"]
        to_extract.faults = json_dict["faults"]
        to_extract.game_count = json_dict["game_count"]
        to_extract.xp = json_dict["xp"]
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
            game = memowordrize.from_json(session["game"])
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

@memowordrize_bp.route('/dashboard/games/memowordrize/<int:list_id>')
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
        if index == 0 and game["lesson_id"] == memowordrize_id:
            game = memowordrize(list_result["id"], game["id"], list_result["words"])
            id = game.id
            session['game'] = game.to_json()
            return redirect(url_for('memowordrize.start', session_id=id))
        elif index > 0 and list_result["lessons"][index-1]["completed"] == 1 and game["lesson_id"] == memowordrize_id:
            game = memowordrize(list_result["id"], game["id"], list_result["words"])
            id = game.id
            session['game'] = game.to_json()
            return redirect(url_for('memowordrize.start', session_id=id))
    
    # If the game is not available, return a 404 error
    abort(404)
    
@memowordrize_bp.route('/dashboard/games/memowordrize/<string:session_id>')
def start(session_id):
    """
    Start the game by displaying the game interface
    
    Args:
        session_id (string): The unique identifier of the game
        
    Returns:
        flask.redirect: 
    """
    try:
        if 'game' in session:
            game = memowordrize.from_json(session["game"])
            if not game.current_path:
                current_path = None
            else:
                current_path = game.current_path  
            
            current_path = None
        
            reloaded = True if game.get_remaning_time() < 178 else False
            if session_id == game.id and game.time > str(datetime.datetime.now()):
                session["game"] = game.to_json()
                return render_template('games/memowordrize.html', 
                                    session_id=session_id, 
                                    list_id=game.list_id,
                                    time=game.get_remaning_time(),
                                    xp=game.xp,
                                    current_path=current_path,
                                    reloaded=reloaded)
            return redirect(url_for('memowordrize.index', list_id=game.list_id))
        return redirect(url_for('main.index'))
    except Exception as e:  
        logging.error("An error has occured: " + str(e))
        return "ok"
    
@memowordrize_bp.route('/dashboard/games/memowordrize/<string:session_id>/see_path')
@check_game
def next_path(session_id):
    """
    See the current path of the game
    
    Args:
        session_id (string): The unique identifier of the game
        
    Returns:
        dict: The response of the request
            - code (int): The status code of the request
                -> 200: The current path is accessible
                -> 403: The current path has been seen too many times
                -> 500: An error has occured
            - message (string): The message of the request
            - result (dict): The result of the request
                - tries (int): The number of tries
                - path (list): The path of the game
                - words (list): The shuffled words to place in the path
    """
    try:
        game = memowordrize.from_json(session["game"])
        response = game.see_path()
        session["game"] = game.to_json()
        return response
    except Exception as e:
        logging.error("An error has occured: " + str(e))
        return jsonify({
            "code": 500,
            "message": "Une erreur s'est produite!",
            "result": []
        }), 500

@memowordrize_bp.route('/dashboard/games/memowordrize/<string:session_id>/audio/<string:id>')
@check_game
def audio(session_id, id):
    """
    Generate the audio of a word
    
    Args:
        session_id (string): The unique identifier of the game
        id (string): The unique identifier of the word
        
    Returns:
        flask.Response: The audio of the word
    """
    try:
        game = memowordrize.from_json(session["game"])
        current_game_index = [index for index, item in enumerate(game.current_path["path"]) if item["id"] == id]
        if current_game_index:
            word = game.current_path["path"][current_game_index[0]]["word"]["word"]
            # Generate the audio
            tts = gTTS(word, lang='en')
            # Save the audio in a BytesIO object
            audio_bytes = BytesIO()
            # Write the audio in the BytesIO object
            tts.write_to_fp(audio_bytes)
            # Set the position of the BytesIO object to 0
            audio_bytes.seek(0)
            
            game.current_path["path"][current_game_index[0]]["id"] = str(uuid.uuid4())
            session["game"] = game.to_json()
            time.sleep(1/100) # To avoid session concurrency
            # Return the audio
            return Response(audio_bytes, mimetype="audio/mp3")
        return jsonify({
            "code": 404,
            "message": "Le mot n'a pas été trouvé!",
            "result": []
        }), 404
    except Exception as e:
        logging.error("An error has occured: " + str(e))
        return jsonify({
            "code": 500,
            "message": "Une erreur s'est produite!",
            "result": []
        }), 500
        
@memowordrize_bp.route('/dashboard/games/memowordrize/<string:session_id>/try_case', methods=['POST'])
@check_game
def try_case(session_id):
    """
    Try a case
    
    Args:
        session_id (string): The unique identifier of the game
        
    Returns:
        dict: The response of the request
            - code (int): The status code of the request
                -> 200: The game is ready
                -> 500: An error has occured
            - message (string): The message of the request
            - result (dict): The result of the request
                - tries (int): The number of tries
                - path (list): The path of the game
    """
    try:
        game = memowordrize.from_json(session["game"])
        # Get the data from the request
        data = request.get_json()
        position = data["position"]
        word = data["word"]
        # Try the case
        response = game.check_case(position, word)
        session["game"] = game.to_json()
        time.sleep(1/100) # To avoid session concurrency
        return response
    except Exception as e:
        logging.error("An error has occured: " + str(e))
        return jsonify({
            "code": 500,
            "message": "Une erreur s'est produite!",
            "result": []
        }), 500
        
@memowordrize_bp.route('/dashboard/games/memowordrize/<string:session_id>/check_status')
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
    game = memowordrize.from_json(session["game"])
    return jsonify({
        "code": 200,
        "message": "Le jeu est en cours!",
        "result": {
            "remaining": len(game.words_to_check),
            "time": game.get_remaning_time(),
            "words": game.get_words_checked()
        }
    })