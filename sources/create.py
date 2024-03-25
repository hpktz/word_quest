"""
This module contains the routes for creating a list.

Imports:
    - flask: For handling requests and responses.
    - flask_login: For handling user sessions.
    - root: The root module of the application.
    - json: For parsing and generating JSON data.
    - datetime: For handling dates and times.
    - random: For generating random numbers.
    - logging: For logging errors and other information.
    - profanity: For detecting the presence of profanity in a text.
    - time: For handling time.

Blueprint:
    - create_bp: The blueprint for the routes for creating a list.
"""
from flask import Blueprint, render_template, redirect, url_for, jsonify, request, session, abort
from flask_login import login_user, login_required, logout_user, current_user
from profanity import profanity_detector
from root import *
import random as random
from lxml import html, etree
import requests
import uuid
import re
import json
import logging
import time

create_bp = Blueprint('create', __name__)
"""
The blueprint for the routes for creating a list.

Attributes:
    - create_bp: The blueprint for the routes for creating a list.
    
Routes:
    - /dashboard/create: To display the create page.
    - /dashboard/create/word-box: To display the word box.
    - /dashboard/create/empty-word-box: To display the empty word box.
    - /dashboard/create/search/<string:x>: To search a word in the Collins API.
    - /dashboard/create/add/<string:id>: To add a word to the list under creation.
    - /dashboard/create/remove/<string:id>: To remove a word from the list under creation.
    - /dashboard/create/word-in-list: To display the word in list.
    - /dashboard/create/create-list: To create a list.
    - /dashboard/list/copy/<int:id>: To copy a list.
    - /dashboard/list/copy_link/<string:token>: To copy a list from a link.
"""

class WordList:
    """
    This class represents a list of words.
    
    Attributes:
        - _list: The list of words.
        - _last_searched: The last searched words.
    
    Methods:
        - add: Add a word to the list.
        - remove: Remove a word from the list.
        - get_all: Get all the words in the list.
        - length: Get the length of the list.
        - search: Search a word in the list.
    """
    def __init__(self):
        self._list = []
        self._last_searched = []

    def add(self, id):
        """
        Add a word to the list.

        Args:
            id (string): The ID of the word to add.

        Returns:
            dict: The added word if found in the last searched words, otherwise None.
        """
        for word in self._last_searched:
            if word['id'] == id:
                word['id'] = str(uuid.uuid4())
                self._list.append(word)
                return word
        return None
        
    def remove(self, id):
        """
        Remove a word from the list.

        Args:
            id (string): The ID of the word to remove.

        Returns:
            dict: The removed word if found in the list, otherwise None.
        """
        for word in self._list:
            if word['id'] == id:
                self._list.remove(word)
                return word
        return None
    
    def get_all(self):
        """
        Get all the words in the list.

        Returns:
            list: The list of words.
        """
        return self._list
    
    def length(self):
        """
        Get the length of the list.

        Returns:
            int: The length of the list.
        """
        return len(self._list)
        
    def search(self, searched):
        """
        Memorize the last searched words.

        Args:
            searched (list): The list of searched words.
        """
        self._last_searched = searched
        
        
    def to_json(self):
        """
        Convert the list to JSON.

        Returns:
            dict: The list in JSON.
        """
        return json.dumps({
            "_list": self._list,
            "_last_searched": self._last_searched
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
        word_list = cls()
        word_list._list = data["_list"]
        word_list._last_searched = data["_last_searched"]
        return word_list

    

@create_bp.route('/dashboard/create')
@login_required
def create():
    """
    Display the create page.

    Returns:
        flask.render_template: The create page.
    """
    session['list_under_creation'] = WordList().to_json()
    return render_template('dashboard/create.html')


@create_bp.route('/dashboard/create/word-box')
@login_required
def word_box():
    """
    Display the word box.
    
    Returns:
        flask.render_template: The word box.
    """
    return render_template('dashboard/content/word-box.html')

@create_bp.route('/dashboard/create/empty-word-box')
@login_required
def empty_word_box():
    """
    DIisplay the empty word box.

    Returns:
        flask.render_template: The empty word box.
    """
    return render_template('dashboard/content/empty-word-box.html')

@create_bp.route('/dashboard/create/search/<string:language>/<string:x>')
@login_required
def search(language, x): 
    """
    Search a word in the Collins API.

    Args:
        x (string): The word to search.

    Returns:
        dict: The result of the search.
            - code (int): The status code of the response.
                -> 200: Word found.
                -> 404: Word not found.
                -> 500: Internal server error.
            - title (string): The title of the response.
            - result (list): The list of words if found, otherwise an empty list.

    Raises:
        500: If an error occurs while searching the word.
    """
    # Call the Collins API
    if language == "fr":
        language = "french-english"
    else:
        language = "english-french"
        
    
    # Remove the end spaces
    x = x.strip()    
        
    url = f"https://api.collinsdictionary.com/api/v1/dictionaries/{language}/entries/{x}_1"
    headers = {
        "Accept": "application/json",
        "accessKey": os.environ.get("COLLINS_API_KEY"),
    }
    if session['list_under_creation'] is None:
        return jsonify({"code": 403, "title": "Access forbidden", "result": []}), 403

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        resp_json = response.json()

        def get_text_recursive(element):
            text = element.text or ""
            for child in element:
                text += get_text_recursive(child)
            return text

        # Parse the response (HTML)
        dom = html.fromstring(resp_json["entryContent"])
        # Start html code analysis
        entries = dom.xpath("//div[@class='hom']")
        senses = []
        for entry in entries:
            for index, sense in enumerate(entry.iterchildren()):
                # Skip if not an HtmlElement
                if not isinstance(sense, html.HtmlElement):
                    continue

                # Create the array with basic informations
                if sense.get("class") == "sense":
                    type = entry.xpath(".//span[@class='pos']/text()")[0]
                    if type == "masculine noun" or type == "feminine noun":
                        type = "noun"
                    array = {
                        "id": str(uuid.uuid4()),
                        "type": type,
                        "word": x if language == "english-french" else "",
                        "french_translation": x if language == "french-english" else "",
                        "examples": [],
                        "french_translation_examples": []
                    }
                    # Retrieve the french translation
                    word = sense.xpath("./span[@class='cit lang_fr']") if language == "english-french" else sense.xpath("./span[@class='cit lang_en-gb']")
                    if word:
                        word = word[0].xpath("./span[@class='quote']")
                        
                        word = ''.join(text for text in word[0].xpath(".//text()[not(parent::*[@class='hi' or @class='lbl'])]"))
                        word = re.sub(r'[^a-zA-ZÀ-ÿ\s-]', '', word)
                        if language == "english-french":
                            array["french_translation"] = word.strip()
                        else:
                            array["word"] = word.strip()
                    else:
                        continue
                else:
                    continue

                # Retrieve the examples
                for example in sense.iterchildren():
                    # Skip if not an HtmlElement
                    if not isinstance(example, html.HtmlElement):
                        continue
                    if language == "english-french":
                        if example.get("id", "").split(".")[0] == f"{x}_1":
                            # Select all the french elements
                            french_examples = example.xpath(".//span[@class='cit lang_fr']")
                            for f in french_examples:
                                # Check if there is many french examples for one english example
                                if get_text_recursive(f.getprevious()).encode("utf-8") == b', ':
                                    continue
                                array["french_translation_examples"].append(get_text_recursive(f))

                            # Explore all the english elements
                            english1 = example.xpath(".//span[@class='orth']/text()")
                            if english1:
                                array["examples"].append(english1[0])
                            english2 = example.xpath("./span[@class='quote']/text()")
                            if english2:
                                array["examples"].append(english2[0])
                            english3 = example.xpath(".//span[@class='cit']/span[@class='quote']/text()")
                            for e in english3:
                                array["examples"].append(e)
                                               
                if language == "french-english":
                    for example in sense.xpath(".//span[@class='re']"):
                        # Select all the english elements
                        english_examples = example.xpath(".//span[@class='cit lang_en-gb']")
                        for f in english_examples:
                            # Check if there is many english examples for one french example
                            if get_text_recursive(f.getprevious()).encode("utf-8") == b', ':
                                continue
                            array["examples"].append(get_text_recursive(f))

                        # Explore all the french elements
                        french1 = example.xpath(".//span[@class='orth']/text()")
                        if french1:
                            array["french_translation_examples"].append(french1[0])
                        french2 = example.xpath("./span[@class='quote']/text()")
                        if french2:
                            array["french_translation_examples"].append(french2[0])
                        french3 = example.xpath(".//span[@class='cit']/span[@class='quote']/text()")
                        for e in french3:
                            array["french_translation_examples"].append(e)
                        

                senses.append(array)

        # Memorize the last searched words
        wordList = WordList.from_json(session['list_under_creation'])
        wordList.search(senses)
        session['list_under_creation'] = wordList.to_json()

        if len(senses) == 0:
            return jsonify({"code": 404, "title": "Word not found", "result": []})
        else:
            return jsonify({"code": 200, "title": "Word found", "result": senses})
    except requests.exceptions.HTTPError as err:
            return jsonify({"code": 404, "title": "Word not found", "result": []})
    except Exception as e:
        logging.error("Error while searching word: " + str(e), exc_info=True)
        abort(500)
    
        
@create_bp.route('/dashboard/create/add/<string:id>')
@login_required
def add_to_list(id):
    """
    Add a word to the list under creation.

    Args:
        id (string): The ID of the word to add.

    Returns:
        dict: The result of the addition.
            - code (int): The status code of the response.
                -> 200: Word added.
                -> 404: Word not found.
                -> 500: Internal server error.
            - title (string): The title of the response.
            - result (dict): The added word if found in the last searched words, otherwise None.
    """
    if session['list_under_creation'] is None:
        return jsonify({"code": 403, "title": "Access forbidden", "result": []}), 403

    wordList = WordList.from_json(session['list_under_creation'])
    added = wordList.add(id)
    session['list_under_creation'] = wordList.to_json()
    time.sleep(1/1000) # To avoid session concurrency
    
    if added is not None:
        return jsonify({"code": 200, "title": "Word added", "result": added}), 200

    return jsonify({"code": 404, "title": "Word not found", "result": []}), 404

@create_bp.route('/dashboard/create/remove/<string:id>')
@login_required
def remove_from_list(id):
    """
    Remove a word from the list under creation.

    Args:
        id (string): The ID of the word to remove.

    Returns:
        dict: The result of the removal.
            - code (int): The status code of the response.
                -> 200: Word removed.
                -> 404: Word not found.
                -> 500: Internal server error.
            - title (string): The title of the response.
            - result (dict): The removed word if found in the list, otherwise None.
    """
    if session['list_under_creation'] is None:
        return jsonify({"code": 403, "title": "Access forbidden", "result": []}), 403

    wordList = WordList.from_json(session['list_under_creation'])
    removed = wordList.remove(id)
    session['list_under_creation'] = wordList.to_json()
    time.sleep(1/1000) # To avoid session concurrency
    
    if removed is not None:
        return jsonify({"code": 200, "title": "Word removed", "result": removed}), 200

    return jsonify({"code": 404, "title": "Word not found", "result": []}), 404

@create_bp.route('/dashboard/create/word-in-list')
@login_required
def word_in_list():
    """
    Display the word in list.

    Returns:
        flask.Response: The word in list.
    """
    return render_template('dashboard/content/word-in-list.html')

@create_bp.route('/dashboard/create/create-list', methods=['POST'])
@login_required
def create_list():
    """
    Create a list.

    Returns:
        dict : The result of the creation.
            - code (int): The status code of the response.
                -> 200: List created.
                -> 400: Bad request.
                -> 403: Access forbidden.
                -> 500: Internal server error.
            - title (string): The title of the response.
            - message (string): The message of the response.
                -> Only if the status code is 400.

    Raises:
        500: If an error occurs while creating the list.
    """
    if session['list_under_creation'] is None:
        return jsonify({"code": 403, "title": "Access forbidden"}), 403
    
    wordList = WordList.from_json(session['list_under_creation'])
    
    if wordList.length() < 5:
        return jsonify({"code": 400, "title": "Bad request", "message": "Ajoutez au minimum 5 mots à votre liste"})

    data = request.json

    # Get the data
    name = data.get('name')
    desc = data.get('desc')
    time = data.get('time')
    xp = data.get('xp')
    game = data.get('game')
    reminder = data.get('reminder')
    stats = data.get('stats')
    public = data.get('public')

    conn = None
    cursor = None
    try: 
        conn = create_connection()
        cursor = conn.cursor()    
        # Check if the list name and description are valid
        regex = re.compile(r'^[a-zA-Z0-9#\'\s,.!?À-ÿ]+$')
        if not regex.match(name):
            return jsonify({"code": 400, "title": "Bad request", "message": "Caractères invalides"})
        
        if len(desc) > 0 and not regex.match(desc):
            return jsonify({"code": 400, "title": "Bad request", "message": "Caractères invalides"})
        
        if len(name) > 50 or len(desc) > 500:
            return jsonify({"code": 400, "title": "Bad request", "message": "Trop de caractères"})
        
        if len(name) == 0:
            return jsonify({"code": 400, "title": "Bad request", "message": "Nom invalide"})
        
        if profanity_detector(name) or profanity_detector(desc):
            return jsonify({"code": 400, "title": "Bad request", "message": "Contenu inapproprié"})
        
        # Check if time, xp and game are valid
        if int(time) not in [1, 3, 5] or int(xp) not in [10, 20, 30] or int(game) not in [1, 2, 3]:
            time = 5
            xp = 10
            game = 1
        
        # Check if reminder, stats and public are valid
        if not isinstance(reminder, bool) or not isinstance(stats, bool) or not isinstance(public, bool):
            reminder = False
            stats = False
            public = False
            
        # Create the list
        cursor.execute("INSERT INTO lists (title, description, tgt_time, tgt_xp, tgt_games, notif_remind, notif_stats, public, user_id, creator_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                        (name, desc, time, xp, game, reminder, stats, public, current_user.id, current_user.id))
        
        # Get the list ID
        list_id = cursor.lastrowid
        
        # Add the words to the list
        wordList = WordList.from_json(session['list_under_creation'])
        for word in wordList.get_all():
            cursor.execute("INSERT INTO list_content (word, word_type, trans_word, examples, trans_examples, list_id) VALUES (%s, %s, %s, %s, %s, %s)", 
                            (word['word'], word['type'], word['french_translation'], json.dumps(word['examples']), json.dumps(word['french_translation_examples']), list_id))
            
        # Get the user level
        with open(str(os.getenv("DIRECTORY_PATH")) + 'static/games-data.json') as json_file:
            levels = json.load(json_file)

        levels_difficulty = [1, 1, 2, 2, 3]
        # Choose the levels according to the levels difficulty
        data_levels = []
        for levelnb, level in enumerate(levels_difficulty):
            possible_levels = []
            for key, value in enumerate(levels):
                if value["difficulty"] == level and value not in data_levels:
                    possible_levels.append(value)
            data_levels.append(random.choice(possible_levels))
                    
        # Add the levels to the list
        for key, level in enumerate(data_levels):
            cursor.execute("INSERT INTO lessons (list_id, lesson_id, odr) VALUES (%s, %s, %s)", 
                            (list_id, level["id"], key+1))
            
        return jsonify({"code": 200, "title": "List created"}), 200
    except mysql.connector.Error as e:
        if conn:
            conn.rollback()
        logging.error("Error while creating list: " + str(e), exc_info=True)
        abort(500)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            

@create_bp.route('/dashboard/list/copy/<int:id>')
@login_required
def copy_list(id):
    """
    Copy a list.

    Args:
        id (int): The ID of the list to copy.

    Returns:
        dict : The result of the copy.
            - code (int): The status code of the response.
                -> 200: List copied.
                -> 400: Bad request.
                -> 403: Access forbidden.
                -> 404: List not found.
                -> 500: Internal server error.
            - title (string): The title of the response.
            - message (string): The message of the response.
                -> Only if the status code is 400.

    Raises:
        500: If an error occurs while copying the list.
    """
    conn = None
    cursor = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        # Check if the list exists
        cursor.execute("SELECT * FROM lists WHERE id = %s", (id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({"code": 404, "title": "List not found"}), 404
        
        is_yours = False
        if result[1] is not None:
            is_yours = any(list["id"] == result[1] for list in current_user.get_lists())
            
        if is_yours or result[2] == current_user.id:
            return jsonify({"code": 400, "title": "Bad request", "message": "Vous ne pouvez pas copier votre propre liste"}), 400
        
        # Create the list
        cursor.execute("INSERT INTO lists (title, description, tgt_time, tgt_xp, tgt_games, notif_remind, notif_stats, public, user_id, creator_id, initial_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                        (result[7], result[8], result[11], result[9], result[10], result[12], result[13], result[4], current_user.id, result[3], result[0]))
        
        list_id = cursor.lastrowid
        
        # Create the list content
        cursor.execute("SELECT * FROM list_content WHERE list_id = %s", (id,))
        result = cursor.fetchall()
        columns = [i[0] for i in cursor.description]
        
        for word in result:
            word = dict(zip(columns, word))
            cursor.execute("INSERT INTO list_content (word, word_type, trans_word, examples, trans_examples, list_id) VALUES (%s, %s, %s, %s, %s, %s)", 
                            (word['word'], word['word_type'], word['trans_word'], word['examples'], word['trans_examples'], list_id))
        
        user_level = current_user.lvl
        with open(str(os.getenv("DIRECTORY_PATH")) + 'static/games-data.json') as json_file:
            levels = json.load(json_file)
        
        levels_difficulty = [1, 1, 2, 2, 3]
        # Choose the levels according to the levels difficulty
        data_levels = []
        for levelnb, level in enumerate(levels_difficulty):
            possible_levels = []
            for key, value in enumerate(levels):
                if value["difficulty"] == level and value not in data_levels:
                    possible_levels.append(value)
            data_levels.append(random.choice(possible_levels))
        
        # Add the levels to the list
        for key, level in enumerate(data_levels):
            cursor.execute("INSERT INTO lessons (list_id, lesson_id, odr) VALUES (%s, %s, %s)", 
                            (list_id, level["id"], key+1))
        
        return jsonify({"code": 200, "title": "List copied"}), 200
        
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error("Error while copying list: " + str(e), exc_info=True)
        abort(500)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        
        
@create_bp.route('/dashboard/list/copy_link/<string:token>')
@login_required
def copy_list_link(token):
    """
    Copy a list from a link.

    Args:
        token (string): The token of the list to copy.

    Returns:
        flask.redirect: The index page.

    Raises:
        500: If an error occurs while copying the list.
    """
    conn = None
    cursor = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        # Check if the list exists and if the token is still valid
        cursor.execute("SELECT * FROM lists WHERE shared_token = %s AND shared_expires > NOW()", (token,))
        result = cursor.fetchone()
        if not result:
            return redirect(url_for('main.index'))
        initial_id = result[0]
        
        is_yours = False
        if result[1] is not None:
            is_yours = any(list["id"] == result[1] for list in current_user.get_lists())
            
        if is_yours or result[2] == current_user.id:
            return jsonify({"code": 400, "title": "Bad request", "message": "Vous ne pouvez pas copier votre propre liste"}), 400
        
        # Create the list
        cursor.execute("INSERT INTO lists (title, description, tgt_time, tgt_xp, tgt_games, notif_remind, notif_stats, public, user_id, creator_id, initial_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                        (result[7], result[8], result[11], result[9], result[10], result[12], result[13], result[4], current_user.id, result[3], result[0]))
        
        list_id = cursor.lastrowid
        
        # Create the list content
        cursor.execute("SELECT * FROM list_content WHERE list_id = %s", (initial_id,))
        result = cursor.fetchall()
        columns = [i[0] for i in cursor.description]
        
        for word in result:
            word = dict(zip(columns, word))
            cursor.execute("INSERT INTO list_content (word, word_type, trans_word, examples, trans_examples, list_id) VALUES (%s, %s, %s, %s, %s, %s)", 
                            (word['word'], word['word_type'], word['trans_word'], word['examples'], word['trans_examples'], list_id))
        
        user_level = current_user.lvl
        with open(str(os.getenv("DIRECTORY_PATH")) + 'static/games-data.json') as json_file:
            levels = json.load(json_file)
        
        levels_difficulty = [1, 1, 2, 2, 3]
        # Choose the levels according to the levels difficulty
        data_levels = []
        for levelnb, level in enumerate(levels_difficulty):
            possible_levels = []
            for key, value in enumerate(levels):
                if value["difficulty"] == level and value not in data_levels:
                    possible_levels.append(value)
            data_levels.append(random.choice(possible_levels))
        
        # Add the levels to the list
        for key, level in enumerate(data_levels):
            cursor.execute("INSERT INTO lessons (list_id, lesson_id, odr) VALUES (%s, %s, %s)", 
                            (list_id, level["id"], key+1))
        
        return redirect(url_for('main.index', new_list=True))
        
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error("Error while copying list: " + str(e), exc_info=True)
        abort(500)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        
