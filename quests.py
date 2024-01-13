from flask import Blueprint, render_template, redirect, url_for, jsonify, request, session
from flask_login import login_user, login_required, logout_user, current_user
from root import *
import random as random
import logging as logging
from datetime import datetime, timedelta
import locale

locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

quests_bp = Blueprint('quests', __name__)

@quests_bp.route('/dashboard/quests')
@login_required
def quests():
    targets = {"games": 0, "xp": 0,"time": 0}
    
    try:
        for lst in current_user.lists:
            if not all(lesson["completed"] == 1 for lesson in lst["lessons"]):
                targets["games"] += lst["tgt_games"]
                targets["xp"] += lst["tgt_xp"]
                targets["time"] += lst["tgt_time"]
                
        is_there_targets = targets["games"] != 0 or targets["xp"] != 0 or targets["time"] != 0
        
        with create_connection() as conn, conn.cursor() as cursor:
            seven_days_ago = datetime.now() - timedelta(days=7)
            cursor.execute("SELECT DATE(created_at) as day, COUNT(*) as lesson_count,  SUM(xp) as total_xp, SUM(time) as total_time FROM lessons_log WHERE user_id = %s AND DATE(created_at) >= %s GROUP BY day", (current_user.id,seven_days_ago))
            result = cursor.fetchall()
            cursor.execute("SELECT u.id as user_id, u.name as username, SUM(ll.xp) as total_xp, RANK() OVER (ORDER BY SUM(ll.xp) DESC) as user_rank FROM users u JOIN lessons_log ll ON u.id = ll.user_id GROUP BY u.id, u.name ORDER BY total_xp DESC;")
            ranking = cursor.fetchall()
            
        results = []
        progress = 0
        for i in range(7):
            day = datetime.now().date() - timedelta(days=i)
            day_result = next((res for res in result if res[0] == day), None)
            if day_result:
                progress += day_result[1] + day_result[2] + day_result[3]
                target_achieved = day_result[2] >= targets["xp"] and day_result[3] >= targets["time"] and day_result[1] >= targets["games"]
            else:
                target_achieved = False
            results.append({
                "day": day.strftime("%A").capitalize(),
                "lesson_count": day_result[1] if day_result else 0,
                "total_xp": day_result[2] if day_result else 0,
                "total_time": day_result[3] if day_result else 0,
                "target_achieved": target_achieved
            })
                
        results[0]["target_lesson_count"] = targets["games"]
        results[0]["target_lesson_count_achieved"] = results[0]["lesson_count"] >= targets["games"]
        results[0]["target_xp"] = targets["xp"]
        results[0]["target_xp_achieved"] = results[0]["total_xp"] >= targets["xp"]
        results[0]["target_time"] = targets["time"]
        results[0]["target_time_achieved"] = results[0]["total_time"] >= targets["time"]        
        
        max_xp = max(res["total_xp"] for res in results)
        if max_xp == 0:
            max_xp = 1
            
        if progress != 0 and targets["games"] != 0 and targets["xp"] != 0 and targets["time"] != 0:
            progress = round(progress/(targets["games"]*7 + targets["xp"]*7 + targets["time"]*7)*100, 0)
                
        results.reverse()
        
        is_there_stats = any(res["lesson_count"] != 0 or res["total_xp"] != 0 or res["total_time"] != 0 for res in results)
       
        # Get the user rank with the ranking
        print(ranking)
        user_rank = 0
        top_ranking = []
        arround_ranking = []
        
        for item, rank in enumerate(ranking):
            if int(rank[0]) == int(current_user.id):
                user_rank = int(rank[3])
                break   
                
        if user_rank > 3:
            top_ranking = ranking[:3]
            arround_ranking = ranking[user_rank-2:user_rank+1]
        elif user_rank <= 3 and user_rank != 0:
            top_ranking = []
            arround_ranking = ranking[:5]     
        else:
            user_rank = "Pas classé"
       
        return render_template(
            'dashboard/quests.html', 
            stats=results,
            is_there_stats=is_there_stats,
            is_there_targets=is_there_targets,
            max_xp=max_xp, 
            progress=progress,
            user_rank=user_rank,
            top_ranking=top_ranking,
            arround_ranking=arround_ranking
        )
    
    except mysql.connector.Error as e:
        logging.error("Error while fetching quests: " + str(e), exc_info=True)
        return render_template('dashboard/quests.html')
