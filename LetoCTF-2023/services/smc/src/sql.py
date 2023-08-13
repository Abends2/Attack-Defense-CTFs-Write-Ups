from src import app
from urllib.parse import urlparse
import psycopg2


class db:
    def __init__(self):
        cs = urlparse(app.config["POSTGRES_CONNECT"])
        self.conn = psycopg2.connect(dbname=cs.path[1:],
                               user=cs.username,
                               password=cs.password,
                               host=cs.hostname,
                               port=cs.port)
        self.conn.autocommit = True

    def init_db(self):
        with self.conn.cursor() as cursor:
            cursor.execute(open("src/schema.sql", "r").read())

    def get_user_by_id(self, userid):
        results = []
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %d" % (int(userid), ))
            results = cursor.fetchall()
        if results == [] or results[0] == []:
            results = None
        return results

    def get_all_users(self):
        results = []
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT id, username FROM users")
            results = cursor.fetchall()
        if results == [] or results[0] == []:
            results = None
        return results

    def get_user_by_name(self, username):
        results = []
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username, ))
            results = cursor.fetchall()
        if results == [] or results[0] == []:
            results = None
        return results

    def insert_user(self, username, password, personal_data):
        results = None
        with self.conn.cursor() as cursor:
            cursor.execute("INSERT INTO users (username, password, personal_data) VALUES (%s, %s, %s) RETURNING id", (username, password, personal_data ))
            results = cursor.fetchone()[0]
        return results
    
    def get_doctor_by_id(self, docid):
        results = []
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM doctors WHERE id = %d" % (int(docid), ))
            results = cursor.fetchall()
        if results == []:
            results = None
        return results
    
    def get_doctor_by_name(self, docname):
        results = []
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM doctors WHERE name = '%s'" % (docname, ))
            results = cursor.fetchall()
        if results == [] or results[0] == []:
            results = None
        return results

    def get_all_doctors(self):
        results = []
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT id, name FROM doctors")
            results = cursor.fetchall()
        if results == [] or results[0] == []:
            results = None
        return results

    def insert_doctor(self, username, password, personal_data):
        results = None
        with self.conn.cursor() as cursor:
            cursor.execute("INSERT INTO users (username, password, personal_data) VALUES (%s, %s, %s) RETURNING id", (username, password, personal_data ))
            results = cursor.fetchone()[0]
        return results

    def create_appointment(self, userid, doctor_name, fio, ins_num, time):
        results = None
        with self.conn.cursor() as cursor:
            cursor.execute("INSERT INTO appointments (user_id, doctor_name, fio, insurance_num, time) VALUES (%s, %s, %s, %s, %s) RETURNING id", (userid, doctor_name, fio, ins_num, time, ))
            results = cursor.fetchone()[0]
        return results

    def get_appointment_by_id(self, appid):
        results = []
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM appointments WHERE id = %d" % (int(appid), ))
            results = cursor.fetchall()
        if results == []:
            results = None
        return results

    def get_appointments_by_userid(self, userid):
        results = []
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM appointments WHERE user_id = %d" % (int(userid), ))
            results = cursor.fetchall()
        if results == []:
            results = None
        return results
