from flask import Blueprint, render_template, redirect, url_for, jsonify, request, session, abort
from flask_login import login_user, login_required, logout_user, current_user
from profanity import profanity_detector
from root import *
import json
from datetime import datetime, timedelta
import random as random
import logging
import re
import uuid

test_bp = Blueprint('test', __name__)

@test_bp.route('/test')
def test():
    conn = None
    cursor = None
    try:
        conn = create_connection() # Create a connection to the database.
        cursor = conn.cursor() # Create a cursor to execute SQL queries.
        cursor.execute("""
        SELECT l.*, 
            JSON_ARRAYAGG(
                JSON_OBJECT(
                    'id', e.id,
                    'word', e.word,
                    'type', e.word_type,
                    'examples', e.examples,
                    'trans_word', e.trans_word,
                    'trans_examples', e.trans_examples
                )
            ) AS words,
        FROM lists l 
        JOIN list_content e ON e.list_id = l.id 
        WHERE l.user_id = 55
        GROUP BY l.id;
        """)
        results = cursor.fetchall()
        return results
        results = cursor.fetchall() # Execute the SQL query.
        columns = [col[0] for col in cursor.description] # Get the columns of the result.
        results = [{columns[i]: result[i] for i in range(len(columns))} for result in results] # Convert the result to a dictionary.
        for result in results:
            result["created_at"] = result["created_at"].date().strftime("%d/%m/%Y") # Convert the created_at column to a string.
            result["updated_at"] = result["updated_at"].date().strftime("%d/%m/%Y") # Convert the created_at column to a string.
            
            result["words"] = json.loads(result["words"]) # Convert the words column to a list.
            result["lessons"] = json.loads(result["lessons"])

            for word in result["words"]:
                word["examples"] = json.loads(word["examples"]) # Convert the examples column to a list.
                word["trans_examples"] = json.loads(word["trans_examples"])
            
            return results # Return the user's lists.
        print(results)
        return jsonify(results)
    except mysql.connector.Error as e:
        print(e)
        logging.error("Error in test :" + str(e))
        return jsonify([])
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()