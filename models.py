from flask_login import UserMixin
from root import *
import json
from datetime import datetime

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id
        try:
            with create_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
                user = cursor.fetchone()
                cursor.close()
                if not user:
                    self.name = None
                    self.birthday = None
                    self.email = None
                    self.lvl = None
                    self.lists = None
                    return

                name = user[1]
                birthday = user[2]
                email = user[7]
                lvl = user[3]

                with conn.cursor() as cursor:
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

                    with conn.cursor() as cursor:
                        cursor.execute('SELECT id, word, type, examples, trans_word, trans_examples FROM list_content WHERE list_id = %s', (result["id"],))
                        columns = [column[0] for column in cursor.description]
                        words = cursor.fetchall()

                    for word in words:
                        result["words"].append({
                            "word": word[1],
                            "type": word[2],
                            "examples": json.loads(word[3]),
                            "trans_word": word[4],
                            "trans_examples": json.loads(word[5])
                        })

                    with conn.cursor() as cursor:
                        cursor.execute('SELECT id, lesson_id, odr, completed FROM lessons WHERE list_id = %s', (result["id"],))
                        columns = [column[0] for column in cursor.description]
                        lessons = cursor.fetchall()

                    for lesson in lessons:
                        result["lessons"].append(dict(zip(columns, lesson)))

                    results.append(result)

                self.name = name
                self.birthday = birthday
                self.email = email
                self.lvl = lvl
                self.lists = results

        except Exception as e:
            print(e)
            self.name = None
            self.birthday = None
            self.email = None
            self.lvl = None
            self.lists = None
    def get_id(self):
        return str(self.id)

    @property
    def is_authenticated(self):
        return True