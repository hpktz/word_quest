""" 
This module contains the User class, which is used to represent a user in the application.

Imports:
    - flask_login: For the UserMixin and AnonymousUserMixin classes.
    - root: For the create_connection function.
    - json: For the json.loads function.
    - datetime: For the datetime class.
    - logging: For logging errors.
"""
from flask_login import UserMixin, AnonymousUserMixin
from root import *
import json
from datetime import datetime
import logging

class User(UserMixin):
    """ 
    This class is used to represent a user in the application.
    
    Attributes:
        - id: The user's id.
        - name: The user's name.
        - birthday: The user's birthday.
        - email: The user's email.
        - lvl: The user's level.
        - picture: The user's picture.
        - mfa: Whether the user has 2FA enabled.
        - public: Whether the user's profile is public.
        
    Methods:
        - get_lists: Returns the user's lists.
        - get_likes: Returns the lists the user has liked.
        - get_lives: Returns the user's lives.
        - get_id: Returns the user's id.
        - is_authenticated: Returns whether the user is authenticated.
    """
    def __init__(self, user_id, name, birthday, email, lvl, picture, mfa, public):
        self.id = user_id
        self.name = name
        self.birthday = birthday
        self.email = email
        self.lvl = lvl
        self.picture = picture
        self.mfa = mfa
        self.public = public
                
    def get_lists(self):
        """
        This method is used to get the user's lists.

        Returns:
            dict: A dictionary containing the user's lists.
        """
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
                lessons.lesson_data AS lessons
            FROM lists l 
            JOIN (
                SELECT list_id, JSON_ARRAYAGG(
                    JSON_OBJECT(
                        'id', le.id,
                        'lesson_id', le.lesson_id,
                        'odr', le.odr,
                        'completed', le.completed
                    )
                ) AS lesson_data
                FROM lessons le
                GROUP BY list_id
            ) AS lessons ON lessons.list_id = l.id
            JOIN list_content e ON e.list_id = l.id 
            WHERE l.user_id = 55
            GROUP BY l.id;
            """)
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
        except Exception as e:
            logging.error("Error in models :" +str(e))    
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                
    def get_likes(self):
        """
        This method is used to get the lists the user has liked.
        
        Returns:
            list: A list containing the lists the user has liked.
        """
        conn = None
        cursor = None
        try:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT list_id FROM list_likes WHERE user_id = %s', (self.id,)) # Execute the SQL query.
            lists = cursor.fetchall()
            return [lst[0] for lst in lists] # Return the lists the user has liked.
        except Exception as e:
            logging.error(e)
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                
    def get_lives(self):
        """
        This method is used to get the user's lives.
        
        Returns:
            int: The user's lives.
        """
        conn = None
        cursor = None
        try:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(CASE WHEN transaction_type = 'lives' THEN transaction ELSE 0 END) \
                AS sum_lives FROM user_statements WHERE user_id = %s LIMIT 1;", (self.id,)) # Execute the SQL query.
            lives = cursor.fetchone()
            return lives[0] # Return the user's lives.
        except Exception as e:
            logging.error(e)
            return 0
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                
    def get_id(self):
        return str(self.id)

    @property
    def is_authenticated(self):
        return True
    
class AnonymousUserMixin(AnonymousUserMixin):
    def __init__(self):
        self.name = None
        self.birthday = None
        self.email = None
        self.lvl = None
        self.picture = None
        self.mfa = None
        self.public = None
        self.lists = None
        
    def get_id(self):
        return None

    @property
    def is_authenticated(self):
        return False