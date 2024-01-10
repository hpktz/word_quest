from flask import Blueprint, render_template, redirect, url_for, jsonify, request
from flask_login import login_user, login_required, logout_user, current_user
from root import *
import json
from datetime import datetime
import random as random

main_bp = Blueprint('main', __name__)

@main_bp.route('/dashboard')
@login_required
def index():
    start_date = datetime.now()
    end_date = datetime(1970, 1, 1)
    for list in current_user.lists:
        created_at = datetime.strptime(str(list["created_at"]), "%d/%m/%Y")
        if created_at < start_date:
            start_date = created_at
        if created_at > end_date:
            end_date = created_at
        
        progress = 0
        for lesson in list["lessons"]:
            if lesson["completed"] == 1:
                progress += 1 
        if progress == 0:
            list["progress"] = 5
            continue
        list["progress"] = progress / len(list["lessons"]) * 100

    start_date = start_date.date().strftime("%Y-%m-%d")
    end_date = end_date.date().strftime("%Y-%m-%d")

    with open('static/daytime-tips.json') as json_file:
        tips = json.load(json_file)

    tip = tips[random.randint(0, len(tips) - 1)]    
    
    return render_template('dashboard/dashboard.html', daytime_tip=tip, lists=current_user.lists, start_date=start_date, end_date=end_date)

@main_bp.route('/dashboard/games/<int:list_id>')
@login_required
def list(list_id):
    try:
        list_result = [l for l in current_user.lists if l["id"] == list_id][0]  
        games_result = []

        with open('static/games-data.json') as json_file:
            games_data = json.load(json_file)

        status = None
        list_result["lessons"] = sorted(list_result["lessons"], key=lambda k: k['odr'])
        for game in list_result["lessons"]:
            game_data = [g for g in games_data if g["id"] == game["lesson_id"]][0]
            if game["completed"] == 1:
                status = "completed"
            elif status == "waiting":
                status = "blocked"
            elif status == "blocked":
                status = status
            else:
                status = "waiting"

            game_result = {
                "id": game["id"],
                "list_id": list_result["id"],
                "lesson_id": game["lesson_id"],
                "ord": game["odr"],
                "name": game_data["name"],
                "short_desc": game_data["short_desc"],
                "img": game_data["img"],
                "url": game_data["url"],
                "status": status,
                "completed": game["completed"]
            }
            games_result.append(game_result)
            
        return render_template('dashboard/content/game-trail-template.html', list=list_result, games=games_result)
    except Exception as e:
        print(e)
        return render_template('dashboard/content/game-trail-empty-template.html')

@main_bp.route('/dashboard/delete/<int:list_id>')
@login_required
def delete(list_id):
    cursor = None
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM lists WHERE id = %s", (list_id,))
        conn.commit()
        return redirect(url_for('main.index'))
    except Exception as e:
        print(e)
        return redirect(url_for('main.index'))
    finally:
        if cursor:
            cursor.close()
        close_connection(conn)  