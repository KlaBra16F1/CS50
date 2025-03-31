from cs50 import SQL
from flask import redirect, render_template, session
from functools import wraps
import random
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
import datetime as dt
from markdown import markdown
import re

# Variables
db = SQL("sqlite:///database2.db.bak")
ROLES = ["admin","maintainer"]

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DAY = dt.timedelta(days=1)


# SQL Functions

# USERS

def get_users():
    users = db.execute("SELECT u_id,name,role FROM users;")
    db._disconnect()
    return users

def get_user(u_id):
    user = db.execute("SELECT COUNT(u_id) AS count FROM users WHERE u_id = ?;", u_id)
    db._disconnect()
    if int(user[0]["count"]) == 1:
        return True
    return False

def add_user(name, hash, role):
    db.execute("INSERT INTO users (name, hash, role) VALUES (?, ?, ?);", name, hash, role)
    db._disconnect()

def delete_user(u_id):
    db.execute("BEGIN TRANSACTION;")
    db.execute("DELETE FROM users WHERE u_id = ?;", u_id)
    db.execute("DELETE FROM user_questions WHERE u_id = ?;", u_id)
    db.execute("COMMIT;")
    db._disconnect()
    

def login_user(username, password):
    user = db.execute("SELECT u_id, name, hash, role FROM users WHERE name = ?", username)
    db._disconnect()
    if user == None or len(user) != 1:
        return None, None, None, "User not found."
    elif check_password_hash(user[0]["hash"], password) == False:
            return None, None, None, "Invalid password."
    else:
        return user[0]["name"], user[0]["u_id"], user[0]["role"], None
    
def check_username(user):
    users = db.execute("SELECT u_id FROM users WHERE name = ?;", user)
    db._disconnect() 
    return len(users)

def register_user(username, password, confirm):
    password_pattern = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[@ # $ % ^ & + =]).{8,}$"
    if check_username(username) > 0:
        return {"error": "user exists"}
    if len(username) not in range(4,16):
        return {"error": "username is too short or too long"}
    
    if re.match(".*(?=[\\W])",username):
        return {"error": "illegal characters in username"}
    
    if len(password) < 8:
        return {"error": "password too short"}
    
    if not re.match(password_pattern,password):
        return {"error": "password not secure"}
    
    if password != confirm:
        return {"error": "passwords don't match"}
    
    add_user(username, generate_password_hash(password),"user")
    return {"success": f"User {username} succesfully created. Please login."}
    




    
# TOPICS

def get_topics():
    topics = db.execute("SELECT t.t_id, topic, (SELECT COUNT(q.q_id) FROM questions q, subtopics s WHERE q.s_id = s.s_id AND s.t_id = t.t_id) AS count FROM topics t ORDER BY topic;")
    db._disconnect()
    return topics

def add_topic(new_topic):
    db.execute("INSERT INTO topics (topic) values (?);", new_topic)
    db._disconnect()

def get_subtopics(t_id):
    subtopics =  db.execute("SELECT s_id, subtopic, (SELECT COUNT(q.q_id) FROM questions q, subtopics sc WHERE q.s_id = sc.s_id AND sc.s_id = s.s_id) AS count FROM subtopics s WHERE t_id = ? ORDER BY subtopic;", t_id)
    db._disconnect()
    return subtopics

def add_subtopic(t_id, new_subtopic):
    db.execute("INSERT INTO subtopics (t_id, subtopic) VALUES (?, ?);", t_id, new_subtopic)
    db._disconnect()

# QUESTIONS

def get_questions(t_id, s_id):
    if t_id is None or t_id =="":
        questions = db.execute("SELECT t.topic, s.subtopic,q.question, q.q_id, q.difficulty, q.isMultipleChoice FROM questions q INNER JOIN subtopics s USING (s_id) INNER JOIN topics t USING (t_id);")
        db._disconnect()
        return questions
    elif s_id is None or s_id == "":
        questions = db.execute("SELECT t.topic, s.subtopic,q.question, q.q_id, q.difficulty, q.isMultipleChoice FROM questions q INNER JOIN subtopics s USING (s_id) INNER JOIN topics t USING (t_id) WHERE t.t_id = ?;", t_id)
        db._disconnect()
        return questions
    else:
        questions = db.execute("SELECT t.topic, s.subtopic,q.question, q.q_id, q.difficulty, q.isMultipleChoice FROM questions q INNER JOIN subtopics s USING (s_id) INNER JOIN topics t USING (t_id) WHERE t.t_id = ? AND s.s_id = ?", t_id, s_id)
        db._disconnect()
        return questions
   

def add_question(s_id, question, difficulty, isMultipleChoice):
    db.execute("INSERT INTO questions (s_id, question, difficulty, isMultipleChoice) values (?, ?, ?, ?)", s_id, question, difficulty, isMultipleChoice)
    q_id = db.execute("SELECT q_id FROM questions WHERE question = ? AND s_id = ?;", question, s_id)
    db._disconnect()
    return q_id[0]

def update_question(q_id, question, multiple):
    db.execute("BEGIN TRANSACTION;")
    db.execute("UPDATE questions SET question = ?, isMultipleChoice = ? WHERE q_id = ?;", question, multiple, q_id)
    changes = db.execute("SELECT changes();")
    db.execute("COMMIT;")
    db._disconnect()
    return changes[0]


def delete_question(q_id):
    db.execute("BEGIN TRANSACTION;")
    db.execute("DELETE FROM answers WHERE q_id = ?;", q_id)
    answers = db.execute("SELECT changes();")
    db.execute("DELETE FROM questions WHERE q_id = ?;", q_id)
    questions = db.execute("SELECT changes();")
    db.execute("COMMIT;")
    db._disconnect()
    

    return questions[0]["changes()"], answers[0]["changes()"]

# ANSWERS

def get_answers(q_ids):
    answers = db.execute("SELECT row_number() OVER (order by random()) AS random, q_id, a_id, answer, comment, is_true FROM answers WHERE q_id IN (?) ORDER BY q_id, random;", q_ids)
    db._disconnect()
    return answers

def add_answers(answers):
    changes = 0
    db.execute("BEGIN TRANSACTION;")
    for answer in answers:
        db.execute("INSERT INTO answers (q_id, answer, comment, is_true) values (?, ?, ?, ?);", int(answer["q_id"]), answer["answer"], answer["comment"], int(answer["true"]))
        change = db.execute("SELECT changes();")
        changes += change[0]["changes()"]
    db.execute("COMMIT;")
    db._disconnect()
    return changes





# TESTS

def create_test(t_id, s_id, count):
    
    if count == "":
        count = None
    else:
        count = int(count)

    questions = get_questions(t_id, s_id)
    questions = list(questions)
    random.shuffle(questions)
    questions = questions[0:count]
    q_ids = [q_id["q_id"] for q_id in questions]
    answers = get_answers(q_ids)
    return questions, answers

def get_questions_result(q_ids):
    questions = db.execute("SELECT q_id, question, isMultipleChoice FROM questions WHERE q_id IN (?);", q_ids)
    return questions

def verify_test(u_id,test):
    update_db = None
    # Check user
    if not (u_id is None or u_id == ""):
        update_db = True if get_user(int(u_id)) == True else None

    now = dt.datetime.today().strftime("%Y-%m-%d")

    questions = []
    for q in test:
        questions.append(q)

    answers = db.execute("SELECT q_id, (SELECT COUNT(*) FROM answers b WHERE a.q_id = b.q_id) as count,a_id , answer FROM answers a WHERE q_id IN (?) AND is_true = 1;", questions)
    
     
    for q in test:
        right_answers = [a["a_id"] for a in answers if a["q_id"] == int(q)]
        right_answers = set(right_answers)
        right_count = len(right_answers)
        user_answers = set(test[q])
        user_right = user_answers & right_answers
        user_right_count = len(user_right)
        wrong_answers = user_answers - right_answers
        wrong_answers = len(wrong_answers)
        passed = 0 if wrong_answers > 0 or user_right_count < right_count else 1
        # Using fail for an update counter in db
        if update_db is True:
            exists = db.execute("SELECT count(*) AS count FROM user_questions WHERE u_id = ? AND q_id = ?;", u_id, int(q))
            if len(exists) == 1 and exists[0]["count"] == 1:
                db.execute("UPDATE user_questions SET timesDone = timesDone + 1, timesRight = timesRight + ?, lastDate = ? WHERE u_id = ? AND q_id = ?;", passed, now, u_id, int(q))
            else:
                db.execute("INSERT INTO user_questions (u_id, q_id, timesDone, timesRight, lastDate) VALUES (?, ?, ?, ?, ?);", u_id, int(q), 1, passed, now)

# Tools

def add_markdown(data, *args):
    output = []
    for d in data:
        d = dict(d)
        #d["answer"] = markdown(d["answer"])
        for a in args:
            d[a] = markdown(d[a]) if d[a] is not None else ''
        output.append(d)
    return output


# Website Functions

def login_required(f):
    """
    Decorate routes to require login.
    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def admin_required(f):
    """
    Decorate routes to require login.
    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None or session["role"] != ROLES[0]:
            return ("",401)
        return f(*args, **kwargs)

    return decorated_function

def maintainer_required(f):
    """
    Decorate routes to require login.
    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None or session["role"] not in ROLES:
            return ("",401)
        return f(*args, **kwargs)

    return decorated_function





    


