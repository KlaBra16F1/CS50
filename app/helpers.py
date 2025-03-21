from cs50 import SQL
from flask import redirect, render_template, session
from functools import wraps
import sqlite3
from werkzeug.security import check_password_hash

# Variables
db = SQL("sqlite:///database.db.bak")
ROLES = ["admin","maintainer"]

# SQL Functions

def get_users():
    users = db.execute("SELECT u_id,name,role FROM users;")
    return users

def add_user(name, hash, role):
    db.execute("INSERT INTO users (name, hash, role) VALUES (?, ?, ?);", name, hash, role)

def delete_user(u_id):
    db.execute("DELETE FROM users WHERE u_id = ?;", u_id)

def login_user(username, password):
    user = db.execute("SELECT u_id, name, hash, role FROM users WHERE name = ?", username)
    if user == None or len(user) != 1:
        return None, None, "User not found."
    elif check_password_hash(user[0]["hash"], password) == False:
            return None, None, "Invalid password."
    else:
        return user[0]["u_id"], user[0]["role"], None

def get_topics():
    topics = db.execute("SELECT t_id, topic FROM topics;")
    return topics

def add_topic(new_topic):
    db.execute("INSERT INTO topics (topic) values (?);", new_topic)

def get_subtopics(t_id):
    subtopics =  db.execute("SELECT s_id, subtopic FROM subtopics WHERE t_id = ? ORDER BY subtopic", t_id)
    return subtopics
def add_subtopic(t_id, new_subtopic):
    db.execute("INSERT INTO subtopics (t_id, subtopic) VALUES (?, ?);", t_id, new_subtopic)

def get_questions(t_id, s_id):
    if s_id == None or s_id == "":
        questions = db.execute("SELECT t.topic, s.subtopic,q.question, q.q_id FROM questions q INNER JOIN subtopics s USING (s_id) INNER JOIN topics t USING (t_id) WHERE t.t_id = ?;", t_id)
        return questions
    
    questions = db.execute("SELECT t.topic, s.subtopic,q.question, q.q_id FROM questions q INNER JOIN subtopics s USING (s_id) INNER JOIN topics t USING (t_id) WHERE t.t_id = ? AND s.s_id = ?", t_id, s_id)
    return questions

def add_question(s_id, question, difficulty, isMultipleChoice):
    db.execute("INSERT INTO questions (s_id, question, difficulty, isMultipleChoice) values (?, ?, ?, ?)", s_id, question, difficulty, isMultipleChoice)
    q_id = db.execute("SELECT q_id FROM questions WHERE question = ? AND s_id = ?;", question, s_id)
    return q_id[0]

def get_answers(q_ids):
    answers = db.execute("SELECT q_id, a_id, answer, comment, is_true FROM answers WHERE q_id IN (?);", q_ids)
    return answers

def add_answers(answers):
    db.execute("BEGIN TRANSACTION;")
    for answer in answers:
        db.execute("INSERT INTO answers (q_id, answer, comment, is_true) values (?, ?, ?, ?);", int(answer["q_id"]), answer["answer"], answer["comment"], int(answer["true"]))
    db.execute("COMMIT;")



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





    


