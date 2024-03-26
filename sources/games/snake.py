"""
This module contains the routes and functions to manage the snake game

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
    - math: for using ceil function
    
Blueprints:
    - snake_bp: The blueprint of the snake game
"""

from flask import Blueprint, render_template, redirect, url_for, jsonify, request, session, abort, make_response, Response
from flask_login import login_user, login_required, logout_user, current_user
from root import *
import random as random
import datetime as datetime
import math as math
import uuid as uuid
import json
import time as time
import math as math
from functools import wraps

import logging


snake_bp = Blueprint('snake', __name__)
"""
The blueprint of the snake game

Attributes:
    -snake_bp: The blueprint of the snake game

Routes:
    - /dashboard/games/snake/<int:list_id>: Initialize the game and redirect to the game interface
    - /dashboard/games/snake/<string:session_id>: Start the game by displaying the game interface
    - /dashboard/games/snake/<string:session_id>/check_status: Check if the game is still in progress
    - /dashboard/games/snake/<string:session_id>/getWord: Get a word and the coordinate of each letter
    - /dashboard/games/snake/<string:session_id>/check_coo Check if the Javascript coordinate correspond to the Python coordinate
"""

# The id of the snake lesson
snake_id = 1

class snake():
    """
    Represents a snake game
    
    Attributes:
        - id (string): The unique identifier of the game
        - list_id (int): The id of the list
        - lesson_id (int): The id of the lesson
        - words (list): The words of the lesson
        - shuffle (list): The words of the lesson mixed
        - time (string): The time when the game ends
        - total_time: The duration of the game
        - start (string): The time when the game started
        - current_word (dict): The current word
        - xp (int): the xp earned
        - finalChecking (list): the list of letters coordinates
        - allLetter (list): the list of all letter in the words of the list
        - word_find (int): the number of word find
        
    Methods:
        - newWord: Get a new word
        - getcoordinate: Gets the coordinates of one letter
        - checkingCoo: Check if the Javascript coordinates correspond to the Python coordinate
        - get_remaning_time: Get the remaining time
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
        while len(self.words) > 6:
            self.words.pop(random.randint(0, len(words)-1))
        self.shuffle = random.sample(self.words, len(self.words))
        self.current_word = {}
        self.total_time = len(words) * 23
        self.time = str(datetime.datetime.now() + datetime.timedelta(seconds=self.total_time))
        self.start = str(datetime.datetime.now())
        self.finalChecking = []
        self.xp = 0
        self.allLetters = ""
        for i in self.shuffle:
            self.allLetters += i['word']
        self.word_find = 0



    def newWord(self):
        """
        Take a new word in the list of the user

        Returns:
        dict: The response of the request
            - code (int): The status code of the request
                -> 200: the word has been recovered
                -> 500: An error has occured
            - message (string): The message of the request
            - result (dict): The result of the request
                - coo (list): The list of dictionnary which represent each coordinate of each letter in the word
                - space_positions (list): the position of spaces in the word
                - frensh (str): The the translation of the word
        """
        try:
            coLetters = []
            self.current_word = self.shuffle.pop()

            # Joins the word and retrieves the space index if the word is a compound word
            word_choosen = ''.join([i for i in self.current_word["word"] if i != " "])
            spaces_positions = [i for i, l in enumerate(self.current_word["word"]) if l == " "]

            # Get the translation of the word
            frensh_word = self.current_word['trans_word']

            # Get the coordinates of each letter
            for letter in word_choosen:
                coLetters.append(self.getcoordinate(coLetters, letter.upper() ))
            self.finalChecking = coLetters

            # Append rock if the word is too small
            while len(coLetters) < 16:
                coLetters.append(self.getcoordinate(coLetters, 'rock'))

            return jsonify({
                'code': 200,
                'message': 'ok',
                'result': {'coo': coLetters,
                        'space_positions': spaces_positions,
                        'frensh': frensh_word}
            })
        except Exception as e:
            logging.error("An error has occured: " + str(e))
            return jsonify({
                    "code": 500,
                    "message": "Une erreur s'est produite!",
                    "result": []
            })
    
    def getcoordinate(self,list, l):
        """
        Gets the coordinates of one letter

        Args:
            list: the list of the coordinates of each letter in the current word
            l: the letter to which add coordinates
        
        Returns:
            a dictionnary with the letter, her x position and her y positions  
        """

        # Take random coordinate in the snake grid
        xpos = math.floor(random.random() * 15) * 32 + 9
        ypos = math.floor(random.random() * 15 + 1) * 32 - 4
        alreadyGet = False

        # Check if the list of coordinate already contains the random coordinate
        if list == []:
            return {'letter': l,'x': xpos, 'y': ypos}
        else:
            for Letter in list:
                if xpos == Letter['x'] and ypos == Letter['y'] or (xpos == 233 and ypos == 252):
                    alreadyGet = True
                    break
        
        # Get new coordinates if already taken
        if alreadyGet:
            return self.getcoordinate(list, l)
        
        else:
            return {'letter': l, 'x': xpos, 'y': ypos}

            

    def checkingCoo(self,list):
        """
        Check if the Javascript coordinates correspond to the Python coordinate

        Args:
            list: The list of coordinates retrieved in Javascript
        
        Returns:
        dict: The response of the request
            - code (int): The status code of the request
                -> 200: checking successfully completed
                -> 500: An error has occured
            - message (string): The message of the request
            - result (dict): The result of the request
                - xp (int): xp earned with the current word
                - xpTot (list): total xp earned
        """
        try:
            xpWord = 0
            if list is not None:
                for i in range(len(list)):
                    # Check that the coordinates of each letter (retrieves in Javascript) correspond to the Python coordinates in order
                    if self.finalChecking[i]['x'] != int(list[i]['x']) or self.finalChecking[i]['y'] != int(list[i]['y']):
                        faute = False
                        for j in range(len(list)):
                            # Go back over the list of coordinates to check whether the user really did get the wrong letter, or whether it's a word with the same letter several times over
                            if self.finalChecking[j]['x'] == int(list[i]['x']) and self.finalChecking[j]['y'] == int(list[i]['y']) and self.finalChecking[j]['letter'] == self.finalChecking[i]['letter']:
                                faute = True
                                break
                        # Returns the result if the user really got the wrong letter
                        if not faute:
                            if (math.ceil(xpWord/2)) > 5:
                                xpWord = 10
                            if xpWord == 0:
                                xpWord = 0
                                self.xp += 0
                            else :
                                xpWord = math.ceil(xpWord/2)
                                self.xp += xpWord
                            return jsonify({
                                'code': 200,
                                'message': 'ok',
                                'result': {'xp': 0 if list is None else xpWord,
                                'xpTot': self.xp}
                            })
                    xpWord += 1
                word_choosen = ''.join([i for i in self.current_word["word"] if i != " "])
                if xpWord == len(word_choosen):
                    self.word_find += 1
                # Calculating xp earned
                if (math.ceil(xpWord/2)) > 5:
                    xpWord = 10
                if xpWord == 0:
                    xpWord = 0
                    self.xp += 0
                else :
                    xpWord = math.ceil(xpWord/2)
                    self.xp += xpWord

            # End the game if there are no more words in the list
            if(len(self.shuffle) == 0):
                return self._end_game(xpWord)
            
            else:
                return jsonify({
                'code': 200,
                'message': 'ok',
                'result': {'xp': 0 if list is None else xpWord,
                        'xpTot': self.xp}
            }) 
        except Exception as e:
            logging.error("An error has occured: " + str(e))
            return jsonify({
                    "code": 500,
                    "message": "Une erreur s'est produite!",
                    "result": []
            })

    def get_remaning_time(self):
        """
        Get the remaining time
        
        Returns:
            int: The remaining time in seconds
        """
        return round((datetime.datetime.strptime(self.time, '%Y-%m-%d %H:%M:%S.%f') - datetime.datetime.now()).total_seconds())
    
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
        
    def _end_game(self, xp_last_word):
        """
        End the game and save the results

        Args:
            xp_last_word: The experience points gained with the last word
        
        Returns:
            dict: The response of the request
                - code (int): The status code of the request
                    -> 201: The game is ended
                    -> 500: An error has occured
                - message (string): The message of the request
                - result (dict): The result of the request
                    - time (int): The time when the game started
                    - lost_lives (int): The number of lost lives 
                    - xp (int): The experience points gained
                    - xpAnim (int): The experience points gained with the last word
        Raises:
            Exception: An error has occured
        """
        conn = None
        cursor = None
        try:
            conn = create_connection()  
            cursor = conn.cursor()
            
            # Calculate the time passed
            time_passed = datetime.datetime.now() - datetime.datetime.strptime(self.start, '%Y-%m-%d %H:%M:%S.%f')
            time_passed = round(time_passed.total_seconds())
                
            # Lose a life if winning experience points isn't enough
            if self.word_find < 4:
                lives_to_lose = 1 
            else:
                lives_to_lose = 0
            while lives_to_lose > 0:
                self._lose_life()
                lives_to_lose -= 1
            
            if self.word_find < 4:
                lives_to_lose = 1 
            else:
                lives_to_lose = 0
            
            # Reduces the amount of xp gained if the game are already completed
            cursor.execute("SELECT * FROM lessons_log WHERE user_id = %s AND lesson_id = %s", (current_user.id, self.lesson_id))
            is_already_completed = cursor.fetchall()
            if is_already_completed:
                self.xp = 2*self.xp//3

            # Update the lesson as completed
            if lives_to_lose == 0:
                cursor.execute("UPDATE lessons SET completed = 1 WHERE id = %s", (self.lesson_id,))
                        
            # Save the results in the database
            cursor.execute("INSERT INTO lessons_log (user_id, list_id, lesson_id, xp, lost_lives, time) VALUES (%s, %s, %s, %s, %s, %s)", (current_user.id, self.list_id, self.lesson_id, self.xp, lives_to_lose, time_passed))
            cursor.execute("INSERT INTO user_statements SET user_id= %s, transaction_type = 'xp', transaction = %s", ( current_user.id, self.xp))
            conn.commit()
            response = jsonify({
                "code": 201,
                "message": "Le jeu est terminé!",
                "result": {
                    "time": time_passed,
                    "lost_lives": lives_to_lose,
                    "xpAnim": xp_last_word,
                    "xp": self.xp,
                    "xpTot": self.xp
                }
            })
            response = make_response(response, 201)
            session.pop('game', None)
            return response
        except Exception as e:
            logging.error("An error has occured: " + str(e))
            return jsonify({
                "code": 500,
                "message": "Une erreur s'est produite!",
                "result": []
            })
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
        to_extract.start = json_dict["start"]
        to_extract.shuffle = json_dict["shuffle"]
        to_extract.finalChecking = json_dict["finalChecking"]
        to_extract.current_word = json_dict["current_word"]
        to_extract.xp = json_dict["xp"]
        to_extract.total_time = json_dict["total_time"]
        to_extract.word_find = json_dict["word_find"]
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
            game = snake.from_json(session["game"])
            # Check if the game is still in progress
            if session_id != game.id or game.time < str(datetime.datetime.now()):
                response = game._end_game(0)
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

@snake_bp.route('/dashboard/games/snake/<int:list_id>')
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
        if index == 0 and game["lesson_id"] == snake_id:
            game = snake(list_result["id"], game["id"], list_result["words"])
            id = game.id
            session['game'] = game.to_json()
            return redirect(url_for('snake.start', session_id=id))
        elif index > 0 and list_result["lessons"][index-1]["completed"] == 1 and game["lesson_id"] == snake_id:
            game = snake(list_result["id"], game["id"], list_result["words"])
            id = game.id
            session['game'] = game.to_json()
            return redirect(url_for('snake.start', session_id=id))
    
    # If the game is not available, return a 404 error
    abort(404)
@snake_bp.route('/dashboard/games/snake/<string:session_id>')
def start(session_id):
    """
    Start the game by displaying the game interface
    
    Args:
        session_id (string): The unique identifier of the game
        
    Returns:
        flask.redirect: 
    """
    if 'game' in session:
        game = snake.from_json(session["game"])
        reloaded = True if game.get_remaning_time() < game.total_time - 2 else False
        if session_id == game.id and game.time > str(datetime.datetime.now()):
            session["game"] = game.to_json()
            return render_template('games/snake.html', 
                                   session_id=session_id, 
                                   list_id=game.list_id,
                                   time=game.get_remaning_time(),
                                   reloaded=reloaded)
        return redirect(url_for('snake.index', list_id=game.list_id))
    return redirect(url_for('main.index'))

@snake_bp.route('/dashboard/games/snake/<string:session_id>/check_status')
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
    game = snake.from_json(session["game"])
    return jsonify({
        "code": 200,
        "message": "Le jeu est en cours!",
        "result": {}
    })

@snake_bp.route('/dashboard/games/snake/<string:session_id>/getWord')
@check_game
def getWord(session_id):
    """
    Get one word of the user list
    
    Args:
        session_id (string): The unique identifier of the game
        
    Returns:
        flask.Response: The response of the request
    """
    game = snake.from_json(session["game"])
    result = game.newWord()
    session["game"] = game.to_json()
    time.sleep(1/100)
    
    if result.status_code == 201:
        session.pop('game', None)
    
    return result

@snake_bp.route('/dashboard/games/snake/<string:session_id>/check_coo', methods=['POST'])
@check_game
def endChecking(session_id):
    """
    Get one word of the user list
    
    Args:
        session_id (string): The unique identifier of the game
        
    Returns:
        flask.Response: The response of the request
    """
    data = request.get_json()
    coord = data['coo']
    game = snake.from_json(session["game"])
    result = game.checkingCoo(coord)
    session["game"] = game.to_json()
    time.sleep(1/100)
    
    if result.status_code == 201:
        session.pop('game', None)
    
    return result
