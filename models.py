from flask_login import UserMixin
from root import *
import json
from datetime import datetime

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id
        conn = None
        cursor = None
        try:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            user = cursor.fetchone()
            if not user:
                self.name = None
                self.birthday = None
                self.email = None
                self.lvl = None
                self.picture = None
                self.lists = None
                return

            name = user[1]
            birthday = user[2]
            email = user[7]
            lvl = user[3]
            picture = user[8]

            cursor.execute('SELECT * FROM lists WHERE user_id = %s', (user_id,))
            columns = [column[0] for column in cursor.description]
            lists = cursor.fetchall()
            results = []
            for lst in lists:
                result = dict(zip(columns, lst))
                result["created_at"] = result["created_at"].date().strftime("%d/%m/%Y")
                result["updated_at"] = result["updated_at"].date().strftime("%d/%m/%Y")

                result["words"] = []
                result["lessons"] = []

                cursor.execute('SELECT id, word, type, examples, trans_word, trans_examples FROM list_content WHERE list_id = %s', (result["id"],))
                words = cursor.fetchall()

                for word in words:
                    result["words"].append({
                        "word": word[1],
                        "type": word[2],
                        "examples": json.loads(word[3]),
                        "trans_word": word[4],
                        "trans_examples": json.loads(word[5])
                    })

                cursor.execute('SELECT id, lesson_id, odr, completed FROM lessons WHERE list_id = %s', (result["id"],))
                columns_lesson = [column[0] for column in cursor.description]
                lessons = cursor.fetchall()

                for lesson in lessons:
                    result["lessons"].append(dict(zip(columns_lesson, lesson)))

                results.append(result)

            self.name = name
            self.birthday = birthday
            self.email = email
            self.lvl = lvl
            self.picture = picture
            self.lists = results

        except Exception as e:
            if conn:
                conn.rollback()
            self.name = None
            self.birthday = None
            self.email = None
            self.lvl = None
            self.picture = None
            self.lists = None
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