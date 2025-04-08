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
ROLES = ["admin","maintainer","user"]

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
    if check_username(name) != 0:
        return {"error" : "user exists"}
    db.execute("INSERT INTO users (name, hash, role) VALUES (?, ?, ?);", name, hash, role)
    db._disconnect()

def delete_user(u_id):
    db.execute("BEGIN TRANSACTION;")
    db.execute("DELETE FROM user_tests WHERE u_id = ?;", u_id)
    db.execute("DELETE FROM user_questions WHERE u_id = ?", u_id)
    db.execute("DELETE FROM users WHERE u_id = ?;", u_id)
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

def check_user_id(u_id):
    u_id = db.execute("SELECT u_id FROM users WHERE u_id = ?;", u_id)
    db._disconnect() 
    return len(u_id)

def change_password(u_id, old_pw, pw, confirm):
    if verify_password(u_id, old_pw) == 0:
        return {"error": "wrong password"}
    if old_pw == pw:
        return {"error": "new password is old passwword"}
    if pw != confirm:
        return {"error": "new passwords don't match"}
    db.execute("UPDATE users set hash = ? WHERE u_id = ?;", generate_password_hash(pw), u_id)
    changes = db.execute("SELECT changes();")
    db._disconnect()
    if changes[0]["changes()"] != 1:
        return {"error": "database error"}
    return {"success": "Password changed"}

def verify_password(u_id, password):
    pw = db.execute("SELECT hash FROM users WHERE u_id = ?;", u_id)
    db._disconnect()
    return check_password_hash(pw[0]["hash"], password)



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
    
def change_role(u_id, role):
    if role not in ROLES:
        return {"error": "role not available"}
    if session["user_name"] == "admin":
        return {"error": "admin must stay admin"}
    if check_user_id(u_id) != 1:
        return {"error": "unknown user_id"}
    db.execute("UPDATE users set role = ? WHERE u_id = ?;", role, u_id )
    db._disconnect() 
    return {"success": "changed user role"}

def delete_account(u_id, password):
    if session["user_name"] == "admin":
        return {"error": "we need an admin here!"}
    if check_user_id(u_id) != 1:
        return {"error": "user doesn't exist"}
    if verify_password(u_id, password) != 1:
        return {"error": "wrong password"}
    db.execute("BEGIN TRANSACTION;")
    db.execute("DELETE FROM user_tests WHERE u_id = ?;", u_id)
    db.execute("DELETE FROM user_questions WHERE u_id = ?", u_id)
    db.execute("DELETE FROM users WHERE u_id = ?;", u_id)
    db.execute("COMMIT;")
    return {"success": "Good bye."}

def get_userstats(u_id):
    stats = []
    db.execute("BEGIN TRANSACTION;")
    overall = db.execute("SELECT COUNT(DISTINCT t.t_id) AS topics, COUNT(DISTINCT s.s_id) AS subtopics, "
                            "COUNT(uq.timesDone) AS times, AVG(accuracy) AS accuracy, (SELECT COUNT(*) FROM questions) AS total_questions "
                            "FROM user_questions uq INNER JOIN questions q USING (q_id) INNER JOIN subtopics s USING(s_id) INNER JOIN topics t USING(t_id) "
                            "WHERE uq.u_id = ?;", u_id)
    overall = {k:v for (k,v) in overall[0].items()}
    stats.append(overall)
    LIMIT = 3
    top = []
    mostTopic = db.execute("SELECT t.topic, SUM(timesDone) AS times " \
                            "FROM user_questions uq, questions q, subtopics s, topics t " \
                            "WHERE uq.q_id = q.q_id AND q.s_id = s.s_id AND s.t_id = t.t_id AND u_id = ? " \
                            "GROUP BY t.topic ORDER BY times DESC LIMIT ?;", u_id, LIMIT)
    mostSubtopic = db.execute("SELECT t.topic, s.subtopic, SUM(timesDone) AS times FROM user_questions uq, questions q, subtopics s, topics t " \
                                "WHERE uq.q_id = q.q_id AND q.s_id = s.s_id AND s.t_id = t.t_id AND u_id = ? " \
                                "GROUP BY t.topic, s.subtopic ORDER BY times DESC LIMIT ?;", u_id, LIMIT)
    bestTopic= db.execute("SELECT t.topic, AVG(accuracy) AS accuracy " \
                            "FROM user_questions uq, questions q, subtopics s, topics t " \
                            "WHERE uq.q_id = q.q_id AND q.s_id = s.s_id AND s.t_id = t.t_id AND u_id = ? " \
                            "GROUP BY t.topic ORDER BY accuracy DESC LIMIT ?;", u_id, LIMIT)
    bestSubtopic = db.execute("SELECT t.topic, s.subtopic, AVG(accuracy) AS accuracy " \
                                "FROM user_questions uq, questions q, subtopics s, topics t " \
                                "WHERE uq.q_id = q.q_id AND q.s_id = s.s_id AND s.t_id = t.t_id AND u_id = ? " \
                                "GROUP BY t.topic, s.subtopic ORDER BY accuracy DESC LIMIT ?;", u_id, LIMIT)
    if len(mostTopic) > 0:
        for row in range(len(mostTopic)):
            top.append({"mostTopic": mostTopic[row]["topic"],"mostTopicCount": mostTopic[row]["times"], 
                            "mostSubtopic": mostSubtopic[row]["topic"] + "/" + mostSubtopic[row]["subtopic"], "mostSubtopicCount": mostSubtopic[row]["times"],
                            "bestTopic": bestTopic[row]["topic"], "bestTopicAccuracy": bestTopic[row]["accuracy"],
                            "bestSubtopic": bestSubtopic[row]["topic"] + '/' + bestSubtopic[row]["subtopic"], "bestSubtopicAccuracy": bestSubtopic[row]["accuracy"]})
        stats.append(top)
        print(top)
    compare = db.execute("SELECT distinct t.topic, "
                            "(SELECT AVG(uq.accuracy) FROM user_questions uq, questions q, subtopics s WHERE t.t_id = s.t_id AND s.s_id = q.s_id AND q.q_id = uq.q_id AND uq.u_id = ?) AS mystats, "
                            "(SELECT AVG(uq.accuracy) FROM user_questions uq, questions q, subtopics s WHERE t.t_id = s.t_id AND s.s_id = q.s_id AND q.q_id = uq.q_id AND NOT uq.u_id = ?) AS others " \
                            "FROM topics t WHERE mystats NOT NULL ORDER BY mystats DESC;", u_id, u_id)
    db._disconnect()
    
    
    stats.append(compare)
    return stats

def delete_stats(u_id):
    print("cp")
    db.execute("BEGIN TRANSACTION;")
    db.execute("DELETE FROM user_questions WHERE u_id = ?;", u_id)
    count = db.execute("SELECT changes();")
    db.execute("COMMIT;")
    db._disconnect()
    if count[0]["changes()"] > 0:
        return {"success": "Your stats have been cleared."}
    else:
        return {"error": "database error"}


    
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

def delete_topic(t_id):
    deleted = {}
    db.execute("BEGIN TRANSACTION;")
    s_ids = db.execute("SELECT s.s_id FROM topics t, subtopics s WHERE t.t_id = s.t_id AND s.t_id = ?;", t_id)
    s_ids = list(s["s_id"] for s in s_ids)
    q_ids = db.execute("SELECT q_id FROM questions WHERE s_id in (?);", s_ids)
    q_ids = list(q["q_id"] for q in q_ids)
    db.execute("DELETE FROM answers WHERE q_id IN (?);", q_ids)
    changes = db.execute("SELECT changes();")
    deleted["answers"] = changes[0]["changes()"]
    db.execute("DELETE FROM questions WHERE s_id IN (?);", s_ids)
    changes = db.execute("SELECT changes();")
    deleted["questions"] = changes[0]["changes()"]
    db.execute("DELETE FROM subtopics WHERE s_id IN (?)", s_ids)
    changes = db.execute("SELECT changes();")
    deleted["subtopics"] = changes[0]["changes()"]
    db.execute("DELETE FROM topics WHERE t_id = ?;", t_id)
    changes = db.execute("SELECT changes();")
    deleted["topics"] = changes[0]["changes()"]
    db.execute("DELETE FROM user_questions WHERE q_id IN (?);", q_ids)
    changes = db.execute("SELECT changes();")
    deleted["user_stats"] = changes[0]["changes()"]
    db.execute("COMMIT;")
    return deleted

def delete_subtopic(s_id):
    deleted = {}
    db.execute("BEGIN TRANSACTION;")
    q_ids = db.execute("SELECT q_id FROM questions WHERE s_id = ?;", s_id)
    q_ids = list(q["q_id"] for q in q_ids)
    db.execute("DELETE FROM answers WHERE q_id IN (?);", q_ids)
    changes = db.execute("SELECT changes();")
    deleted["answers"] = changes[0]["changes()"]
    db.execute("DELETE FROM questions WHERE s_id = ?;", s_id)
    changes = db.execute("SELECT changes();")
    deleted["questions"] = changes[0]["changes()"]
    db.execute("DELETE FROM subtopics WHERE s_id = ?", s_id)
    changes = db.execute("SELECT changes();")
    deleted["subtopics"] = changes[0]["changes()"]
    db.execute("DELETE FROM user_questions WHERE q_id IN (?);", q_ids)
    changes = db.execute("SELECT changes();")
    deleted["user_stats"] = changes[0]["changes()"]
    db.execute("COMMIT;")
    return deleted

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
        print(s_id)
        questions = db.execute("SELECT t.topic, s.subtopic,q.question, q.q_id, q.difficulty, q.isMultipleChoice FROM questions q INNER JOIN subtopics s USING (s_id) INNER JOIN topics t USING (t_id) WHERE t.t_id = ? AND s.s_id IN (?);", t_id, s_id)
        db._disconnect()
        return questions
    
def get_user_questions(u_id, t_id, s_id):
    if t_id is None or t_id =="":
        questions = db.execute("SELECT row_number() OVER (order by random()) AS random, t.topic, s.subtopic, q.q_id, q.question, q.isMultipleChoice,"
                                "(SELECT timesDONE FROM user_questions WHERE u_id = ? AND q_id = q.q_id ) AS timesDone, "
                                "(SELECT ROUND((CAST(timesRight AS REAL) / CAST(timesDone AS REAL)),2) AS score "
                                "FROM user_questions WHERE u_id = ? AND q_id = q.q_id ) AS score, "
                                "(SELECT lastDate FROM user_questions WHERE u_id = ? AND q_id = q.q_id ) as lastDate "
                                "FROM questions q INNER JOIN subtopics s USING (s_id) INNER JOIN topics t USING (t_id) "
                                "ORDER BY timesDone, lastDate, score, random;",u_id, u_id, u_id)
        db._disconnect()
        return questions
    elif s_id is None or s_id == "":
        questions = db.execute("SELECT row_number() OVER (order by random()) AS random, t.topic, s.subtopic, q.q_id, q.question, q.isMultipleChoice,"
                                "(SELECT timesDONE FROM user_questions WHERE u_id = ? AND q_id = q.q_id ) AS timesDone, "
                                "(SELECT ROUND((CAST(timesRight AS REAL) / CAST(timesDone AS REAL)),2) AS score "
                                "FROM user_questions WHERE u_id = ? AND q_id = q.q_id ) AS score, "
                                "(SELECT lastDate FROM user_questions WHERE u_id = ? AND q_id = q.q_id ) as lastDate "
                                "FROM questions q INNER JOIN subtopics s USING (s_id) INNER JOIN topics t USING (t_id) "
                                "WHERE t.t_id = ? ORDER BY timesDone, lastDate, score, random;",u_id, u_id, u_id, t_id)
        db._disconnect()
        return questions
    else:
        questions = db.execute("SELECT row_number() OVER (order by random()) AS random, t.topic, s.subtopic, q.q_id, q.question, q.isMultipleChoice,"
                                "(SELECT timesDONE FROM user_questions WHERE u_id = ? AND q_id = q.q_id ) AS timesDone, "
                                "(SELECT ROUND((CAST(timesRight AS REAL) / CAST(timesDone AS REAL)),2) AS score "
                                "FROM user_questions WHERE u_id = ? AND q_id = q.q_id ) AS score, "
                                "(SELECT lastDate FROM user_questions WHERE u_id = ? AND q_id = q.q_id ) as lastDate "
                                "FROM questions q INNER JOIN subtopics s USING (s_id) INNER JOIN topics t USING (t_id) "
                                "WHERE t.t_id = ? AND s.s_id IN (?) ORDER BY timesDone, lastDate, score, random;",u_id, u_id, u_id, t_id, s_id)

        return questions


def get_selected_questions(q_ids):
    questions = db.execute("SELECT t.topic, s.subtopic, q_id, question, isMultipleChoice "
                            "FROM questions INNER JOIN subtopics s USING (s_id) INNER JOIN topics t USING (t_id) "
                            "WHERE q_id IN (?);", q_ids)
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
    is_multple_choice(answers[0]["q_id"])
    return changes

def add_answer(q_id, answer, is_true, comment):
    db.execute("INSERT INTO answers (q_id, answer, is_true, comment) VALUES (?, ?, ?, ?);", q_id, answer, is_true, comment)
    changes = db.execute("SELECT changes();")
    db._disconnect()
    is_multple_choice(q_id)
    changes = changes[0]["changes()"]
    msg = {"success": f"Added {changes} answer"}
    if changes != 1:
        msg = {"error": "database error"}
    return msg


def update_answer(q_id, a_id, answer, is_true, comment):
    db.execute("UPDATE answers SET answer = ?, is_true = ?, comment = ? WHERE a_id = ?;", answer, is_true, comment, a_id)
    changes = db.execute("SELECT changes();")
    db._disconnect()
    is_multple_choice(q_id)
    changes = changes[0]["changes()"]
    msg = {"success": f"updated {changes} answer"}
    if changes != 1:
        msg = {"error": "database error"}
    return msg

def delete_answer(a_id, q_id):
    db.execute("DELETE FROM answers WHERE a_id = ?;", a_id)
    changes = db.execute("SELECT changes();")
    db._disconnect()
    is_multple_choice(q_id)
    changes = changes[0]["changes()"]
    msg = {"success": f"Deleted {changes} answer"}
    if changes != 1:
        msg = {"error": "database error"}
    return msg
    
# Special Feature

def is_multple_choice(q_id):
    db.execute("BEGIN TRANSACTION;")
    is_true = db.execute("SELECT COUNT(*) AS count FROM answers WHERE q_id = ? AND is_true = 1", q_id)
    print("i_t:",is_true, q_id)
    if is_true[0]["count"] > 1:
        db.execute("UPDATE questions SET isMultipleChoice = 1 WHERE q_id = ?;", q_id)
    else:
        db.execute("UPDATE questions SET isMultipleChoice = 0 WHERE q_id = ?;", q_id)
    db.execute("COMMIT;")
    db._disconnect()






# TESTS

def create_test(u_id, t_id, s_id, count):
    
    if count == "":
        count = None
    else:
        count = int(count)

    questions = []
    if u_id is None or u_id == "":
        questions = get_questions(t_id, s_id)
        questions = list(questions)
        random.shuffle(questions)
        questions = questions[0:count]
    else:
        questions = get_user_questions(u_id, t_id, s_id)
        questions = list(questions)
        questions = questions[0:count]
        random.shuffle(questions)
    

    q_ids = [q_id["q_id"] for q_id in questions]
    answers = get_answers(q_ids)
    return questions, answers

def get_questions_result(q_ids):
    questions = get_selected_questions(q_ids)
    return questions

def verify_test(u_id,test):
    update_db = None
    is_user = 0
    # Check user
    if not (u_id is None or u_id == ""):
        update_db = True if get_user(int(u_id)) == True else None
        is_user = 1

    now = dt.datetime.today().strftime("%Y-%m-%d")

    questions = []
    for q in test:
        questions.append(q)

    answers = db.execute("SELECT q_id, (SELECT COUNT(*) FROM answers b WHERE a.q_id = b.q_id) as count,a_id , answer FROM answers a WHERE q_id IN (?) AND is_true = 1;", questions)
    # Update teststats only if test is finnisched
    db.execute("UPDATE teststats set testsMade = testsMade + 1, forUser = forUser + ?", is_user)
    db._disconnect()
     
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
                db._disconnect()
            else:
                db.execute("INSERT INTO user_questions (u_id, q_id, timesDone, timesRight, lastDate) VALUES (?, ?, ?, ?, ?);", u_id, int(q), 1, passed, now)
                db._disconnect()

def save_test(u_id, test_name, questions):
    questions = ','.join(str(q) for q in questions)
    db.execute("INSERT INTO user_tests (u_id, test_name, questions) VALUES (?, ?, ?)", u_id, test_name, questions)
    count = db.execute("SELECT changes()")
    db._disconnect()
    if count[0]["changes()"] != 1:
        return {"error": "database error"}
    
    return {"success": "test saved"}

def delete_test(u_id, ut_id):
    db.execute("DELETE FROM user_tests WHERE u_id = ? and ut_id = ?", u_id, ut_id)
    count = db.execute("SELECT changes();")
    db._disconnect()
    if count[0]["changes()"] != 1:
        return {"error": "database error"}
    
    return {"success": "test deleted"}


def get_saved_tests(u_id):
    tests = db.execute("SELECT ut_id, test_name, questions FROM user_tests WHERE u_id = ?;", u_id)
    db._disconnect()
    return tests

def get_user_test(u_id, ut_id):
    q_ids = db.execute("SELECT questions FROM user_tests WHERE ut_id = ? AND u_id = ?;", ut_id,u_id)
    q_ids = q_ids[0]["questions"].split(',')
    q_ids = list(int(q) for q in q_ids)
    questions = get_selected_questions(q_ids)
    answers = get_answers(q_ids)
    db._disconnect()
    return questions, answers
    

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
        if session.get("user_id") is None or session["role"] not in ROLES[0]:
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
        if session.get("user_id") is None or session["role"] not in ROLES[:2]:
            return ("",401)
        return f(*args, **kwargs)

    return decorated_function





    


