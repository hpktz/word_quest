from flask_login import UserMixin
from root import *
import json
from datetime import datetime

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id
        conn = None
        try:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            user = cursor.fetchone()
            cursor.close()
            if not user:
                self.name = None
                self.birthday = None
                self.email = None
                self.lvl = None
                self.gems = None
                self.lives = None
                self.lives_wait = None
                self.lists = None
                return
                
            name = user[1]
            birthday = user[2]
            email = user[7]
            lvl = user[3]
            gems = user[4]
            lives = user[5]
            lives_wait = user[6]


            cursor = conn.cursor()
            cursor.execute('SELECT * FROM lists WHERE user_id = %s', (user_id,))
            columns = [column[0] for column in cursor.description]
            lists = cursor.fetchall()
            
            results = []
            for list in lists:
                results.append(dict(zip(columns, list)))
                results[-1]["created_at"] = datetime.utcfromtimestamp(results[-1]["created_at"]).strftime("%d/%m/%Y")
                results[-1]["updated_at"] = datetime.utcfromtimestamp(results[-1]["updated_at"]).strftime("%d/%m/%Y")

            cursor.close()

            for result in results:
                result["words"] = []
                result["lessons"] = []

                cursor = conn.cursor()
                cursor.execute('SELECT id, word, type, examples, trans_word, trans_examples FROM list_content WHERE list_id = %s', (result["id"],))
                columns = [column[0] for column in cursor.description]
                words = cursor.fetchall()
                cursor.close()

                for word in words:
                    result["words"].append({
                        "word": word[1],
                        "type": word[2],
                        "examples": json.loads(word[3]),
                        "trans_word": word[4],
                        "trans_examples": json.loads(word[5])
                    })

                cursor = conn.cursor()
                cursor.execute('SELECT id, lesson_id, odr, completed FROM lessons WHERE list_id = %s', (result["id"],))
                columns = [column[0] for column in cursor.description]
                lessons = cursor.fetchall()
                cursor.close()

                for lesson in lessons:
                    result["lessons"].append(dict(zip(columns, lesson)))

            self.name = name
            self.birthday = birthday
            self.email = email
            self.lvl = lvl
            self.gems = gems
            self.lives = lives
            self.lives_wait = lives_wait
            self.lists = results

        except Exception as e:
            print(e)
            self.name = None
            self.birthday = None
            self.email = None
            self.lvl = None
            self.gems = None
            self.lives = None
            self.lives_wait = None
            self.lists = None

        finally:
            close_connection(conn)

    def get_id(self):
        return str(self.id)

    @property
    def is_authenticated(self):
        return True