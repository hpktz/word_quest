""" 
This module contains the routes for the quests page.

Imports:
    - flask: For handling the routes and rendering the templates.
    - flask_login: For handling the user session.
    - root: For the root functions of the application.
    - random: For generating random numbers.
    - logging: For logging errors.
    - datetime: For manipulating dates and times.
    - locale: For formatting numbers and dates.

Blueprints:
    - quests_bp: The blueprint for the quests routes.
"""

from flask import Blueprint, render_template, redirect, url_for, jsonify, request, session, abort
from flask_login import login_user, login_required, logout_user, current_user
from root import *
import random as random
import logging as logging
from datetime import datetime, timedelta
import locale

quests_bp = Blueprint('quests', __name__)
"""
The blueprint for the quests routes.

Routes:
    - /dashboard/quests: The quests page.
    - /dashboard/quests/reward: The reward page.
"""

@quests_bp.route('/dashboard/quests')
@login_required
def quests():
    """
    Display the quests page.
    
    This function fetches the user's stats and ranking, and renders the quests page.
    
    Returns:
        flask.render_template: The quests page.
        
    Raises:
        flask.render_template: The quests page with no stats.
    """
    targets = {"games": 0, "xp": 0,"time": 0}
    
    conn = None
    cursor = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        # Get the user's targets
        lists = current_user.get_lists()
        current_date = datetime.now().date()
        cursor.execute("SELECT lesson_id FROM lessons_log WHERE user_id = %s GROUP BY lesson_id HAVING DATE(MIN(created_at)) = %s;" , (current_user.id, current_date))
        list_finished_today = cursor.fetchall()
        list_finished_today = [lst[0] for lst in list_finished_today]
        for lst in lists:
            if not all(lesson["completed"] == 1 for lesson in lst["lessons"]) or any(lesson["id"] in list_finished_today for lesson in lst["lessons"]):
                targets["games"] += lst["tgt_games"]
                targets["xp"] += lst["tgt_xp"]
                targets["time"] += lst["tgt_time"]
        
        # Check if there are targets
        is_there_targets = targets["games"] != 0 or targets["xp"] != 0 or targets["time"] != 0
        # Get the user's stats
        seven_days_ago = datetime.now() - timedelta(days=7)
        
        # Get the user's xp, time and lesson count for the last 7 days
        cursor.execute("SELECT DATE(created_at) as day, COUNT(*) as lesson_count,  SUM(xp) as total_xp, \
            SUM(time) as total_time FROM lessons_log \
            WHERE user_id = %s AND DATE(created_at) >= %s GROUP BY day", (current_user.id,seven_days_ago))
        result = cursor.fetchall()
        
        # Get the user's ranking
        cursor.execute("SELECT u.id as user_id, u.picture as user_picture, u.name as username, SUM(ll.xp) as total_xp, \
            RANK() OVER (ORDER BY SUM(ll.xp) DESC) as user_rank FROM users u JOIN lessons_log ll ON u.id = ll.user_id \
            GROUP BY u.id, u.name ORDER BY total_xp DESC;")
        ranking = cursor.fetchall()
        
        # Get the user's reward
        cursor.execute("SELECT * FROM rewards WHERE user_id = %s AND DATE(created_at) = CURDATE()", (current_user.id,))
        reward = cursor.fetchall()
            
        results = []
        progress = 0
        for i in range(7):
            # Get the user's stats for each day
            day = datetime.now().date() - timedelta(days=i)
            day_result = next((res for res in result if res[0] == day), None)
            if day_result:
                progress += day_result[1] + day_result[2] + day_result[3]
                if is_there_targets:
                    target_achieved = day_result[2] >= targets["xp"] and day_result[3]//60 >= targets["time"] and day_result[1] >= targets["games"]
                else:
                    target_achieved = False
            else:
                target_achieved = False
            results.append({
                "day": day.strftime("%A").capitalize(),
                "lesson_count": day_result[1] if day_result else 0,
                "total_xp": day_result[2] if day_result else 0,
                "total_time": day_result[3]//60  if day_result else 0,
                "target_achieved": target_achieved
            })
        
        # Set the targets for the last day  
        results[0]["target_lesson_count"] = targets["games"]
        results[0]["target_lesson_count_achieved"] = results[0]["lesson_count"] >= targets["games"]
        results[0]["target_xp"] = targets["xp"]
        results[0]["target_xp_achieved"] = results[0]["total_xp"] >= targets["xp"]
        results[0]["target_time"] = targets["time"]
        results[0]["target_time_achieved"] = results[0]["total_time"] >= targets["time"]        
        
        # Set the max xp for the progress bar
        max_xp = max(res["total_xp"] for res in results)
        if max_xp == 0:
            max_xp = 1
        
        # Set the progress for the progress bar
        if progress != 0 and targets["games"] != 0 and targets["xp"] != 0 and targets["time"] != 0:
            progress = round(progress/(targets["games"]*7 + targets["xp"]*7 + targets["time"]*7)*100, 0)
                
        results.reverse()
        
        is_there_stats = any(res["lesson_count"] != 0 or res["total_xp"] != 0 or res["total_time"] != 0 for res in results)
       
        # Get the user rank with the ranking
        user_rank = 0
        top_ranking = []
        arround_ranking = []
        
        for item, rank in enumerate(ranking):
            if int(rank[0]) == int(current_user.id):
                user_rank = int(rank[4])
                break   
        
        # Set the top and arround ranking for the UI
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
            arround_ranking=arround_ranking,
            reward=reward
        )
    
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error("Error while fetching quests: " + str(e), exc_info=True)
        return render_template('dashboard/quests.html')
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@quests_bp.route('/dashboard/quests/reward')
@login_required
def reward():
    """
    Display the reward page.
    
    This function checks if the user is eligible for a reward and renders the reward page.

    Returns:
        flask.render_template: The reward page.
        
    Raises:
        500: An error occurred while fetching the rewards.
    """
    conn = None
    cursor = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        # Check if the user already got his reward
        cursor.execute("SELECT * FROM rewards WHERE user_id = %s AND DATE(created_at) = CURDATE()", (current_user.id,))
        rewards = cursor.fetchall()
        if rewards:
            return redirect(url_for('quests.quests'))
        else:
            # Check if the user has completed his targets
            targets = {"games": 0, "xp": 0,"time": 0}
            lists = current_user.get_lists()
            current_date = datetime.now().date()
            cursor.execute("SELECT lesson_id FROM lessons_log WHERE user_id = %s GROUP BY lesson_id HAVING DATE(MIN(created_at)) = %s;" , (current_user.id, current_date))
            list_finished_today = cursor.fetchall()
            list_finished_today = [lst[0] for lst in list_finished_today]
            for lst in lists:
                if not all(lesson["completed"] == 1 for lesson in lst["lessons"]) or any(lesson["id"] in list_finished_today for lesson in lst["lessons"]):
                    targets["games"] += lst["tgt_games"]
                    targets["xp"] += lst["tgt_xp"]
                    targets["time"] += lst["tgt_time"]

            cursor.execute("SELECT COUNT(*), SUM(xp), SUM(time) FROM lessons_log WHERE user_id = %s AND DATE(created_at) = CURDATE()", (current_user.id,))
            result = cursor.fetchall()
            if not result:
                is_eligible = False
            else:
                is_eligible = result[0][0] >= targets["games"] and result[0][1] >= targets["xp"] and result[0][2] >= targets["time"]//60

            # Calculate the reward
            if is_eligible:
                reward = result[0][1] / targets["xp"] * 10
                # Give the reward to the user
                cursor.execute("INSERT INTO rewards (user_id) VALUES (%s)", (current_user.id,))
                cursor.execute("INSERT INTO user_statements (user_id, transaction_type, transaction) VALUES (%s, 'gems', %s)", (current_user.id, reward))
                conn.commit()
                
                # Display the reward animation
                return render_template('dashboard/reward.html', reward=int(reward))
            else:
                return redirect(url_for('quests.quests'))
    
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error("Error while fetching rewards: " + str(e), exc_info=True)
        abort(500)
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()