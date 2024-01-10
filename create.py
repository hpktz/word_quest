from flask import Blueprint, render_template, redirect, url_for, jsonify, request, session
from flask_login import login_user, login_required, logout_user, current_user
from root import *
import random as random
from lxml import html, etree
import requests
import uuid
import re
import json

create_bp = Blueprint('create', __name__)

class List:
    def __init__(self):
        self._list = []
        self._last_searched = []

    def add(self, id):
        for word in self._last_searched:
            if word['id'] == id:
                word['id'] = str(uuid.uuid4())
                self._list.append(word)
                return word
        return None
        
    def remove(self, id):
        for word in self._list:
            if word['id'] == id:
                self._list.remove(word)
                return word
        return None
    
    def get_all(self):
        return self._list
    
    def length(self):
        return len(self._list)
        
    def search(self, searched):
        self._last_searched = searched

    

@create_bp.route('/dashboard/create')
@login_required
def create():
    session['list_under_creation'] = List()
    return render_template('dashboard/create.html')


@create_bp.route('/dashboard/create/word-box')
@login_required
def word_box():
    return render_template('dashboard/content/word-box.html')

@create_bp.route('/dashboard/create/empty-word-box')
@login_required
def empty_word_box():
    return render_template('dashboard/content/empty-word-box.html')

@create_bp.route('/dashboard/create/search/<string:x>')
@login_required
def search(x): 
    url = f"https://api.collinsdictionary.com/api/v1/dictionaries/english-french/entries/{x}_1"
    headers = {
        "Accept": "application/json",
        "accessKey": "LGkl9HMIG0q59zJBitg9FQz9LXMphajPH6dM4QNvMOO1rt7EHuyyWAm6CRQnveK3",
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

        dom = html.fromstring(resp_json["entryContent"])
        entries = dom.xpath("//div[@class='hom']")
        senses = []
        for entry in entries:
            for index, sense in enumerate(entry.iterchildren()):
                if not isinstance(sense, html.HtmlElement):
                    continue

                if sense.get("class") == "sense":
                    array = {
                        "id": str(uuid.uuid4()),
                        "type": entry.xpath(".//span[@class='pos']/text()")[0],
                        "word": x,
                        "french_translation": "",
                        "examples": [],
                        "french_translation_examples": []
                    }
                    word = sense.xpath("./span[@class='cit lang_fr']")
                    if word:
                        array["french_translation"] = get_text_recursive(word[0])
                    else:
                        continue
                else:
                    continue

                # Examples
                for example in sense.iterchildren():
                    if not isinstance(example, html.HtmlElement):
                        continue
                    if example.get("id", "").split(".")[0] == f"{x}_1":
                        french_examples = example.xpath(".//span[@class='cit lang_fr']")
                        for f in french_examples:
                            if get_text_recursive(f.getprevious()).encode("utf-8") == b', ':
                                continue
                            array["french_translation_examples"].append(get_text_recursive(f))

                        english1 = example.xpath(".//span[@class='orth']/text()")
                        if english1:
                            array["examples"].append(english1[0])
                        english2 = example.xpath("./span[@class='quote']/text()")
                        if english2:
                            array["examples"].append(english2[0])
                        english3 = example.xpath(".//span[@class='cit']/span[@class='quote']/text()")
                        for e in english3:
                            array["examples"].append(e)

                senses.append(array)

        session['list_under_creation'].search(senses)

        if len(senses) == 0:
            return jsonify({"code": 404, "title": "Word not found", "result": []})
        else:
            return jsonify({"code": 200, "title": "Word found", "result": senses})
    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 404:
            return jsonify({"code": 404, "title": "Word not found", "result": []})
        elif err.response.status_code == 500:
            return jsonify({"code": 500, "title": "Internal server error", "result": []})
        
@create_bp.route('/dashboard/create/add/<string:id>')
@login_required
def add_to_list(id):
    if session['list_under_creation'] is None:
        return jsonify({"code": 403, "title": "Access forbidden", "result": []}), 403

    added = session['list_under_creation'].add(id)
    if added is not None:
        return jsonify({"code": 200, "title": "Word added", "result": added}), 200

    return jsonify({"code": 404, "title": "Word not found", "result": []}), 404

@create_bp.route('/dashboard/create/remove/<string:id>')
@login_required
def remove_from_list(id):
    if session['list_under_creation'] is None:
        return jsonify({"code": 403, "title": "Access forbidden", "result": []}), 403

    removed = session['list_under_creation'].remove(id)
    if removed is not None:
        return jsonify({"code": 200, "title": "Word removed", "result": removed}), 200

    return jsonify({"code": 404, "title": "Word not found", "result": []}), 404

@create_bp.route('/dashboard/create/word-in-list')
@login_required
def word_in_list():
    return render_template('dashboard/content/word-in-list.html')

@create_bp.route('/dashboard/create/create-list', methods=['POST'])
@login_required
def create_list():
    if session['list_under_creation'] is None:
        return jsonify({"code": 403, "title": "Access forbidden"}), 403
    
    if session['list_under_creation'].length() < 2:
        return jsonify({"code": 400, "title": "Bad request", "message": "Ajoutez au minimum 3 mots à votre liste"})

    data = request.json

    name = data.get('name')
    desc = data.get('desc')
    time = data.get('time')
    xp = data.get('xp')
    game = data.get('game')
    reminder = data.get('reminder')
    stats = data.get('stats')
    public = data.get('public')

    cursor = None
    conn = None
    try: 
        conn = create_connection()
        cursor = conn.cursor()
        
        regex = re.compile(r'^[a-zA-Z0-9\-/😀-🙏]+$')
        if not regex.match(name) or not regex.match(desc):
            return jsonify({"code": 400, "title": "Bad request", "message": "Caractères invalides"})
        
        if len(name) > 50 or len(desc) > 500:
            return jsonify({"code": 400, "title": "Bad request", "message": "Trop de caractères"})
        
        if len(name) == 0:
            return jsonify({"code": 400, "title": "Bad request", "message": "Nom invalide"})
        
        if time not in [5, 10, 15] or xp not in [10, 20, 30] or game not in [1, 2, 3]:
            time = 5
            xp = 10
            game = 1
        
        if not isinstance(reminder, bool) or not isinstance(stats, bool) or not isinstance(public, bool):
            reminder = False
            stats = False
            public = False
            
        cursor.execute("INSERT INTO lists (title, description, tgt_time, tgt_xp, tgt_games, notif_remind, notif_stats, public, user_id, creator_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                       (name, desc, time, xp, game, reminder, stats, public, current_user.id, current_user.id))
        
        list_id = cursor.lastrowid
        
        for word in session['list_under_creation'].get_all():
            cursor.execute("INSERT INTO list_content (word, trans_word, examples, trans_examples, list_id) VALUES (%s, %s, %s, %s, %s)", 
                           (word['word'], word['french_translation'], json.dumps(word['examples']), json.dumps(word['french_translation_examples']), list_id))
            
        user_level = current_user.lvl
        with open('static/games-data.json') as json_file:
            levels = json.load(json_file)
        
        if user_level == 1:
            levels_difficulty = [user_level, user_level, user_level, user_level, user_level+1, user_level+1]
        elif user_level == 5:
            levels_difficulty = [user_level-1, user_level, user_level, user_level, user_level, user_level]
        else:
            levels_difficulty = [user_level-1, user_level, user_level, user_level, user_level+1, user_level+1]
            
        data_levels = []
        for levelnb, level in enumerate(levels_difficulty):
            while len(data_levels) < 6 and level > 0:
                possible_levels = []
                for key, value in enumerate(levels):
                    for data_level in data_levels:
                        if data_level["name"] == value["name"]:
                            break
                    if value["difficulty"] == level:
                            possible_levels.append(value)

                if len(possible_levels) > 0:
                    data_levels.append(random.choice(possible_levels))

                level -= 1

        data_levels = list(reversed(data_levels))
        
        for key, level in enumerate(data_levels):
            cursor.execute("INSERT INTO lessons (list_id, lesson_id, odr) VALUES (%s, %s, %s)", 
                           (list_id, level["id"], key+1))
            
        return jsonify({"code": 200, "title": "List created"}), 200
    except mysql.connector.Error as e:
        print(e)
        return jsonify({"code": 500, "title": "Internal server error"}), 500
    finally:
        if cursor:
            cursor.close()
        close_connection(conn)