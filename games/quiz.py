from flask import Blueprint, render_template, redirect, url_for, jsonify, request, session, abort, make_response, Response
from flask_login import login_user, login_required, logout_user, current_user
from root import *
import random as random
import datetime as datetime
import uuid as uuid
import json
from functools import wraps
import Levenshtein 
from google_images_search import GoogleImagesSearch
from gtts import gTTS
from io import BytesIO
import logging


quiz_bp = Blueprint('quiz', __name__)

quiz_id = 8

quiz_types = [
    {
        "id": 1,
        "type": "simple_question",
        "required": {}
    },
    {
        "id": 2,
        "type": "example_question",
        "required": {
            "example": None,
        } 
    },
    {
        "id": 3,
        "type": "image_question",
        "required": {
            "type": "noun"
        }
    },
    {
        "id": 4,
        "type": "audio_question",
        "required": {
            "example": None,
        }
    }
]

class quiz():
    def __init__(self, list_id, lesson_id, words):
        self.id = str(uuid.uuid4())
        self.list_id = list_id
        self.lesson_id = lesson_id
        self.words = words
        self.words_to_check = words
        self.time = str(datetime.datetime.now() + datetime.timedelta(minutes=2))
        self.start = str(datetime.datetime.now())
        self.current_quiz = None
        self.faults = 0
        
    def check_answer(self, answer):
        correct = False
        if answer == self.current_quiz["answer"]:
            correct = True
        else:
            self.faults += 1
            
        for index, word_to_check in enumerate(self.words_to_check):
            if word_to_check["word"] == self.current_quiz["words"]["word"]:
                self.words_to_check.pop(index)
                if len(self.words_to_check) == 0:
                    return self._end_game()
                else:
                   return self.ask_next_question(correct)

    def ask_next_question(self, correct=False):
        if len(self.words_to_check) > 0:
            word_choosen = random.choice(self.words_to_check)
            word_choosen["examples"] = json.loads(word_choosen["examples"])
            word_choosen["trans_examples"] = json.loads(word_choosen["trans_examples"])
            is_example = word_choosen["examples"]
            is_type_noun = word_choosen["type"] == "noun"
            
            if is_example and is_type_noun:
                lesson_type = random.choice([2, 3, 4])
            elif is_example:
                lesson_type = random.choice([1, 2, 4])
            elif is_type_noun:
                lesson_type = random.choice([1, 3])
            else:
                lesson_type = 1
        
            with open('static/words_alpha.txt') as f:
                words = f.readlines()
            
            audio = ""
            image = ""
            bad_answers = []
            if lesson_type == 1:
                possibilities = [
                    ("Quel est le type du mot suivant: « "+word_choosen["word"]+" » ?", word_choosen["type"]),
                    ("Que signifie le mot suivant: « "+word_choosen["word"]+" » ?", word_choosen["trans_word"])
                ]
                choosen = random.choice(possibilities)
                content = choosen[0]
                answer = choosen[1]
                if content[0:4] == "Quel":
                    types_of_word = ["adjective", "adverb", "conjunction", "interjection", "noun", "preposition", "pronoun", "verb"]
                    bad_answers = [word for word in types_of_word if word != word_choosen["type"]][0:3]
                else:
                    with open('static/mots_alpha.txt', encoding='utf-8') as f:
                        words = f.readlines()

                   
            elif lesson_type == 2:
                content = "Quel mot anglais constitue cet exemple « " + word_choosen["trans_examples"][0] + " » ?"
                answer = word_choosen["word"]
            elif lesson_type == 3:
                content = self.get_image(word_choosen["word"])
                image = content
                answer = word_choosen["word"]
            elif lesson_type == 4:
                content = "/dashboard/games/quiz/"+self.id+"/audio"
                audio = word_choosen["examples"][0]
                answer = word_choosen["word"]
                
            if not bad_answers:
                distances = [(word, Levenshtein.distance(word, answer)) for word in words]
                distances_triees = sorted(distances, key=lambda x: x[1])
                bad_answers = [word[0] for word in distances_triees[1:4]]
            
            html = 'games/quiz-content/'+str(quiz_types[lesson_type-1]["type"])+'.html'
            print(bad_answers)
 
            position = random.randint(1, 4)
            answers = []
            while len(answers) < 4:
                if len(answers) == position-1:
                    answers.append(answer)
                else:
                    answers.append(bad_answers.pop(0))

    
            self.current_quiz = {
                "type": lesson_type,
                "words": word_choosen,
                "answer": position,
                "answers": answers,
                "html": html,
                "content": content,
                "audio": audio,
                "image": image
            }
            
            return jsonify({
                "code": 200,
                "message": "Bonne réponse !" if correct else "Mauvaise réponse !",
                "result": {
                    "html": render_template(html, question_content=content),
                    "answers": answers,
                    "score": len(self.words) - len(self.words_to_check),
                    "time": self.get_remaning_time()
                }
            })
        else:
            return self._end_game()
        
    def get_image(self, word):
        gis = GoogleImagesSearch(os.environ.get('GOOGLE_SEARCH_API_KEY'), os.environ.get('GOOGLE_SEARCH_ENGINE_ID'))
        _search_params = {
            'q': ''+word+'+illustration',
            'num': 1,
            'fileType': 'jpg|gif|png',
            'safe': 'safeUndefined',
            'imgColorType': 'imgColorTypeUndefined',
            'imgType': 'photo',
        }

        gis.search(search_params=_search_params)
        for image in gis.results():
            return image.url
    
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
            # Update the lesson as completed
            cursor.execute("UPDATE lessons SET completed = 1 WHERE id = %s", (self.lesson_id,))
            
            # Calculate the experience points
            time_passed = datetime.datetime.now() - datetime.datetime.strptime(self.start, '%Y-%m-%d %H:%M:%S.%f')
            time_passed = time_passed.total_seconds()
            xp = round((len(self.words)-self.faults)/len(self.words)) * 20
                
            # Lose a life if there are remaining words
            lives_to_lose = 1 if self.faults > 0 else 0
            while lives_to_lose > 0:
                self._lose_life()
                lives_to_lose -= 1
            
            lives_to_lose = 1 if self.faults > 0 else 0
            
            # Save the results in the database
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
        to_extract.current_quiz = json_dict["current_quiz"]
        to_extract.faults = json_dict["faults"]
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
            game = quiz.from_json(session["game"])
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

@quiz_bp.route('/dashboard/games/quiz/<int:list_id>')
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
        if index == 0 and game["lesson_id"] == quiz_id:
            game = quiz(list_result["id"], game["id"], list_result["words"])
            id = game.id
            session['game'] = game.to_json()
            return redirect(url_for('quiz.start', session_id=id))
        elif index > 0 and list_result["lessons"][index-1]["completed"] == 1 and game["lesson_id"] == quiz_id:
            game = quiz(list_result["id"], game["id"], list_result["words"])
            id = game.id
            session['game'] = game.to_json()
            return redirect(url_for('quiz.start', session_id=id))
    
    # If the game is not available, return a 404 error
    abort(404)
    
@quiz_bp.route('/dashboard/games/quiz/<string:session_id>')
def start(session_id):
    """
    Start the game by displaying the game interface
    
    Args:
        session_id (string): The unique identifier of the game
        
    Returns:
        flask.redirect: 
    """
    if 'game' in session:
        game = quiz.from_json(session["game"])
        if not game.current_quiz:
            game.ask_next_question()
            
        if session_id == game.id and game.time > str(datetime.datetime.now()):
            session["game"] = game.to_json()
            return render_template('games/quiz.html', 
                                   session_id=session_id, 
                                   list_id=game.list_id,
                                   time=game.get_remaning_time(),
                                   max_score=len(game.words),
                                   score=len(game.words) - len(game.words_to_check) - game.faults,
                                   question=game.current_quiz["html"],
                                   question_content=game.current_quiz["content"],
                                   answers=game.current_quiz["answers"],
                                   )
        return redirect(url_for('quiz.index', list_id=game.list_id))
    return redirect(url_for('main.index'))

@quiz_bp.route('/dashboard/games/quiz/<string:session_id>/audio')
@check_game
def audio(session_id):
    """
    Get the audio of the game
    
    Args:
        session_id (string): The unique identifier of the game
        
    Returns:
        flask.Response: The response of the request
    """
    game = quiz.from_json(session["game"])
    
    print(game.current_quiz)
    if game.current_quiz["audio"]:
        tts = gTTS(game.current_quiz["audio"], lang='en')
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        
        return Response(audio_bytes, mimetype="audio/mp3")
    return jsonify({
        "code": 404,
        "message": "Le fichier audio a été trouvé!",
        "result": []
    }), 404
    
@quiz_bp.route('/dashboard/games/quiz/<string:session_id>/check/<int:answer>')
@check_game
def check(session_id, answer):
    """
    Check the answer of the game
    
    Args:
        session_id (string): The unique identifier of the game
        answer (int): The answer of the user
        
    Returns:
        flask.Response: The response of the request
    """
    game = quiz.from_json(session["game"])
    response = game.check_answer(answer)
    session["game"] = game.to_json()
    
    if response.status_code == 201:
        session.pop("game", None)
    
    return response

@quiz_bp.route('/dashboard/games/quiz/<string:session_id>/check_status')
@check_game
def check_status(session_id):
    game = quiz.from_json(session["game"])
    return jsonify({
        "code": 200,
        "message": "Le jeu est en cours!",
        "result": {}
    })