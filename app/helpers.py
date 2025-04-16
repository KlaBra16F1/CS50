from cs50 import SQL
from flask import redirect, render_template, session, abort
from functools import wraps
import random
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
import datetime as dt
from markdown import markdown
import re

# Variables
try:
    db = SQL("sqlite:///database/database2.db")
except RuntimeError as e:
    print("Db says", e)
    con = sqlite3.connect("./database/database2.db")
    con.close
    db = SQL("sqlite:///database/database2.db")
    db.execute("BEGIN TRANSACTION;")
    db.execute("CREATE TABLE IF NOT EXISTS users (u_id INTEGER PRIMARY KEY NOT NULL DEFAULT rowid, name TEXT NOT NULL, hash TEXT NOT NULL,role TEXT NOT NULL DEFAULT 'user');")
    db.execute("CREATE TABLE IF NOT EXISTS topics (t_id INTEGER PRIMARY KEY NOT NULL DEFAULT rowid, topic TEXT NOT NULL);")
    db.execute("CREATE TABLE IF NOT EXISTS subtopics (s_id INTEGER PRIMARY KEY NOT NULL DEFAULT rowid, t_id INTEGER, subtopic TEXT NOT NULL, FOREIGN KEY (t_id) REFERENCES topics(t_id));")
    db.execute("CREATE TABLE IF NOT EXISTS questions (q_id INTEGER PRIMARY KEY NOT NULL DEFAULT rowid, s_id INTEGER NOT NULL, question TEXT NOT NULL, difficulty INTEGER DEFAULT 0, isMultipleChoice NUMERIC DEFAULT 0, FOREIGN KEY (s_id) REFERENCES subtopics(s_id));")
    db.execute("CREATE TABLE IF NOT EXISTS answers (a_id INTEGER PRIMARY KEY NOT NULL DEFAULT rowid, q_id INTEGER NOT NULL, answer TEXT NOT NULL, comment TEXT, is_true NUMERIC NOT NULL DEFAULT 0, FOREIGN KEY (q_id) REFERENCES questions(q_id));")
    db.execute("CREATE TABLE IF NOT EXISTS user_questions (u_id INTEGER NOT NULL, q_id INTEGER NOT NULL, timesDone INTEGER NOT NULL, timesRight INTEGER NOT NULL, accuracy REAL GENERATED ALWAYS AS (ROUND(CAST(timesRight AS REAL) / CAST(timesDone AS REAL),2)),lastDate TEXT);")
    db.execute("CREATE TABLE IF NOT EXISTS user_tests (ut_id INTEGER PRIMARY KEY NOT NULL DEFAULT rowid, u_id INTEGER NOT NULL, test_name TEXT NOT NULL ,questions TEXT NOT NULL, FOREIGN KEY (u_id) REFERENCES users(u_id));")
    db.execute("CREATE TABLE IF NOT EXISTS teststats (testsMade integer, forUser integer);")
    db.execute("CREATE INDEX IF NOT EXISTS idx_uq ON user_questions (u_id, q_id);")
    db.execute("INSERT INTO teststats VALUES (0, 0);")
    db.execute("INSERT INTO users (name, hash, role) VALUES ('admin', ?, 'admin');", generate_password_hash('admin'))
    db.execute("COMMIT;")

ROLES = ["admin", "maintainer", "user"]

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
    if get_int(user[0]["count"]) == 1:
        return True
    return False


def add_user(name, hash, role):
    if check_username(name) != 0:
        return {"error": "user exists"}
    db.execute("INSERT INTO users (name, hash, role) VALUES (?, ?, ?);", name, hash, role)
    db._disconnect()
    return {"success": f"User {name} created as {role}."}


def delete_user(u_id):
    if u_id == 1:
        return {"error": "Cant' delete admin account."}
    db.execute("BEGIN TRANSACTION;")
    db.execute("DELETE FROM user_tests WHERE u_id = ?;", u_id)
    db.execute("DELETE FROM user_questions WHERE u_id = ?", u_id)
    db.execute("DELETE FROM users WHERE u_id = ?;", u_id)
    db.execute("COMMIT;")
    count = db.execute("SELECT changes() as changes;")
    db._disconnect()
    if count[0].get("changes") != 1:
        return {"error": "User not found."}
    return {"success": "User deleted."}


def delete_account(u_id, password):
    if session["user_name"] == "admin":
        return {"error": "we need an admin here!"}
    if check_user_id(u_id) != 1:
        return {"error": "User doesn't exist"}
    if verify_password(u_id, password) != 1:
        return {"error": "wrong password"}
    msg = delete_user(u_id)
    return msg


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
    if len(username) not in range(4, 16):
        return {"error": "username is too short or too long"}

    if re.match(".*(?=[\\W])", username):
        return {"error": "illegal characters in username"}

    if len(password) < 8:
        return {"error": "password too short"}

    if not re.match(password_pattern, password):
        return {"error": "password not secure"}

    if password != confirm:
        return {"error": "passwords don't match"}

    add_user(username, generate_password_hash(password), "user")
    return {"success": f"User {username} succesfully created. Please login."}


def change_role(u_id, role):
    if role not in ROLES:
        return {"error": "Role not available"}
    if u_id == 1:
        return {"error": "Admin must stay admin"}
    if check_user_id(u_id) != 1:
        return {"error": "Unknown user"}
    db.execute("UPDATE users set role = ? WHERE u_id = ?;", role, u_id)
    db._disconnect()
    return {"success": "changed user role"}


def get_userstats(u_id):
    stats = []
    overall = db.execute("SELECT COUNT(DISTINCT t.t_id) AS topics, COUNT(DISTINCT s.s_id) AS subtopics, "
                         "COUNT(uq.timesDone) AS times, AVG(accuracy) AS accuracy, (SELECT COUNT(*) FROM questions) AS total_questions "
                         "FROM user_questions uq INNER JOIN questions q USING (q_id) INNER JOIN subtopics s USING(s_id) INNER JOIN topics t USING(t_id) "
                         "WHERE uq.u_id = ?;", u_id)
    overall = {k: v for (k, v) in overall[0].items()}
    stats.append(overall)

    compareTopics = db.execute("SELECT t.t_id, t.topic, COUNT(uq.timesDone) AS questions, SUM(uq.timesDone) AS attempts, AVG(uq.accuracy) AS accuracy, "
                               "(SELECT AVG(uq.accuracy) FROM user_questions uq, questions q, subtopics s WHERE t.t_id = s.t_id AND s.s_id = q.s_id AND q.q_id = uq.q_id AND NOT uq.u_id = ?) as others, "
                               "(SELECT COUNT(q_id) from questions qc, subtopics sc WHERE qc.s_id = sc.s_id AND sc.t_id = t.t_id) as q_count "
                               "FROM user_questions uq, questions q, subtopics s, topics t WHERE uq.q_id = q.q_id AND q.s_id = s.s_id AND s.t_id = t.t_id AND uq.u_id = ? GROUP BY t.t_id, t.topic;", u_id, u_id)
    db._disconnect()

    stats.append(compareTopics)
    return stats


def get_userstats_details(t_id, u_id):
    subtopics = db.execute("SELECT s.s_id, s.subtopic, COUNT(uq.timesDone) AS questions, SUM(uq.timesDone) AS attempts, AVG(uq.accuracy) AS accuracy, "
                           "(SELECT AVG(uq.accuracy) FROM user_questions uq, questions q, subtopics st WHERE uq.q_id = q.q_id AND q.s_id = s.s_id AND st.t_id = s.t_id AND NOT uq.u_id = ?) as others, "
                           "(SELECT COUNT(q_id) from questions qc, subtopics sc WHERE qc.s_id = sc.s_id AND sc.t_id = s.t_id AND s.s_id = qc.s_id) as q_count "
                           " FROM user_questions uq, questions q, subtopics s WHERE uq.q_id = q.q_id AND q.s_id = s.s_id AND s.t_id = ? AND uq.u_id = ? GROUP BY s.s_id, s.subtopic;",  u_id, t_id, u_id)
    db._disconnect()
    return subtopics


def delete_stats(u_id):
    db.execute("BEGIN TRANSACTION;")
    db.execute("DELETE FROM user_questions WHERE u_id = ?;", u_id)
    count = db.execute("SELECT changes();")
    db.execute("COMMIT;")
    db._disconnect()
    if count[0]["changes()"] > 0:
        return {"success": "Your stats have been cleared."}
    else:
        return {"error": "database error"}

# Site-Stats


def get_sitestats():
    stats = []
    q_count = db.execute("SELECT COUNT(*) AS q_count FROM questions;")
    # Usage
    usage = db.execute("SELECT testsMade, forUser FROM teststats;")
    stats.append(usage[0])
    users = db.execute("SELECT role, count(*) AS count FROM users GROUP BY role;")
    # Users
    stats.append(users)
    # Topics - Subtopics - Questions - Answers - Usage
    stats_subtopics = db.execute("SELECT t.topic, s.subtopic, COUNT(distinct q.q_id) AS q_count, COUNT(a.a_id) AS a_count, "
                                 "(SELECT SUM(uq.timesDone) FROM user_questions uq, questions qq WHERE uq.q_id = qq.q_id and qq.s_id = s.s_id) as u_count "
                                 "FROM questions q INNER JOIN answers a USING (q_id) INNER JOIN subtopics s USING (s_id) INNER JOIN topics t USING (t_id) GROUP BY t.topic, s.subtopic ORDER BY topic;")
    db._disconnect()
    topic_list = set(t['topic'] for t in stats_subtopics)
    stats_topics = []
    for t in topic_list:
        td = dict()
        for d in stats_subtopics:
            if d['topic'] == t:
                if d['u_count'] is None:
                    d['u_count'] = 0
                td = {'topic': t, 'q_count': td.get('q_count', 0) + d['q_count'], 'a_count': td.get(
                    'a_count', 0) + d['a_count'], 'u_count': td.get('u_count', 0) + d['u_count']}
        stats_topics.append(td)
    stats_topics = sorted(stats_topics, key=lambda x: x["topic"])
    stats.append(stats_topics)
    stats.append(stats_subtopics)
    stats.append(q_count[0].get("q_count"))
    return stats


def topics_diagramm():
    total = db.execute("SELECT COUNT(q_id) as total FROM questions;")
    total = total[0].get("total") if total[0].get("total") is not None and total[0].get("total") > 0 else 1
    data = db.execute(
        "SELECT ROUND((CAST(COUNT(q.q_id) AS real) / ? * 100),2) AS percent, t.topic AS topic FROM questions q INNER JOIN subtopics s USING (s_id) INNER JOIN topics t USING (t_id) GROUP BY topic;", total)
    db._disconnect()
    return data


def userTopics_diagram():
    total = db.execute("SELECT SUM(timesDone) AS total FROM user_questions;")
    total = total[0].get("total") if total[0].get("total") is not None and total[0].get("total") > 0  else 1
    data = db.execute("SELECT t.topic, ROUND((CAST(SUM(uq.timesDone) AS real) / ? * 100),2) AS percent "
                      "FROM user_questions uq, questions q, subtopics s, topics t "
                      "WHERE uq.q_id = q.q_id AND q.s_id = s.s_id AND s.t_id = t.t_id GROUP BY t.topic;", total) 
    db._disconnect()
    return data


def reset_site_stats():
    db.execute("UPDATE teststats SET testsMade = 0, forUser = 0;")
    db._disconnect()


# TOPICS

def get_topics():
    topics = db.execute(
        "SELECT t.t_id, topic, (SELECT COUNT(q.q_id) FROM questions q, subtopics s WHERE q.s_id = s.s_id AND s.t_id = t.t_id) AS count FROM topics t ORDER BY topic;")
    db._disconnect()
    return topics


def add_topic(new_topic):
    topic = db.execute("SELECT topic FROM topics WHERE topic = ?;", new_topic)
    if len(topic) != 0:
        db._disconnect()
        return {"error": "Topic exists."}
    db.execute("INSERT INTO topics (topic) values (?);", new_topic)
    db._disconnect()
    return {"success": f"Topic {new_topic} created."}


def get_subtopics(t_id):
    subtopics = db.execute(
        "SELECT s_id, subtopic, (SELECT COUNT(q.q_id) FROM questions q, subtopics sc WHERE q.s_id = sc.s_id AND sc.s_id = s.s_id) AS count FROM subtopics s WHERE t_id = ? ORDER BY subtopic;", t_id)
    db._disconnect()
    return subtopics


def add_subtopic(t_id, new_subtopic):
    subtopic = db.execute(
        "SELECT subtopic FROM subtopics WHERE t_id = ? AND subtopic = ?", t_id, new_subtopic)
    if len(subtopic) != 0:
        db._disconnect()
        return {"error": "Subtopic exists."}
    db.execute("INSERT INTO subtopics (t_id, subtopic) VALUES (?, ?);", t_id, new_subtopic)
    db._disconnect()
    return {"success": f"Subtopic {new_subtopic} created."}


def delete_topic(t_id):
    deleted = {}
    db.execute("BEGIN TRANSACTION;")
    s_ids = db.execute(
        "SELECT s.s_id FROM topics t, subtopics s WHERE t.t_id = s.t_id AND s.t_id = ?;", t_id)
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
    if t_id is None or t_id == "":
        questions = db.execute(
            "SELECT t.topic, s.subtopic,q.question, q.q_id, q.difficulty, q.isMultipleChoice FROM questions q INNER JOIN subtopics s USING (s_id) INNER JOIN topics t USING (t_id);")
        db._disconnect()
        return questions
    elif s_id is None or s_id == "":
        questions = db.execute(
            "SELECT t.topic, s.subtopic,q.question, q.q_id, q.difficulty, q.isMultipleChoice FROM questions q INNER JOIN subtopics s USING (s_id) INNER JOIN topics t USING (t_id) WHERE t.t_id = ?;", get_int(t_id))
        db._disconnect()
        return questions
    else:

        questions = db.execute(
            "SELECT t.topic, s.subtopic,q.question, q.q_id, q.difficulty, q.isMultipleChoice FROM questions q INNER JOIN subtopics s USING (s_id) INNER JOIN topics t USING (t_id) WHERE t.t_id = ? AND s.s_id IN (?);", get_int(t_id), s_id)
        db._disconnect()
        return questions


def get_user_questions(u_id, t_id, s_id):
    if t_id is None or t_id == "":
        questions = db.execute("SELECT row_number() OVER (order by random()) AS random, t.topic, s.subtopic, q.q_id, q.question, q.isMultipleChoice,"
                               "(SELECT timesDONE FROM user_questions WHERE u_id = ? AND q_id = q.q_id ) AS timesDone, "
                               "(SELECT ROUND((CAST(timesRight AS REAL) / CAST(timesDone AS REAL)),2) AS score "
                               "FROM user_questions WHERE u_id = ? AND q_id = q.q_id ) AS score, "
                               "(SELECT lastDate FROM user_questions WHERE u_id = ? AND q_id = q.q_id ) as lastDate "
                               "FROM questions q INNER JOIN subtopics s USING (s_id) INNER JOIN topics t USING (t_id) "
                               "ORDER BY timesDone, lastDate, score, random;", u_id, u_id, u_id)
        db._disconnect()
        return questions
    elif s_id is None or s_id == "":
        t_id = get_int(t_id)
        questions = db.execute("SELECT row_number() OVER (order by random()) AS random, t.topic, s.subtopic, q.q_id, q.question, q.isMultipleChoice,"
                               "(SELECT timesDONE FROM user_questions WHERE u_id = ? AND q_id = q.q_id ) AS timesDone, "
                               "(SELECT ROUND((CAST(timesRight AS REAL) / CAST(timesDone AS REAL)),2) AS score "
                               "FROM user_questions WHERE u_id = ? AND q_id = q.q_id ) AS score, "
                               "(SELECT lastDate FROM user_questions WHERE u_id = ? AND q_id = q.q_id ) as lastDate "
                               "FROM questions q INNER JOIN subtopics s USING (s_id) INNER JOIN topics t USING (t_id) "
                               "WHERE t.t_id = ? ORDER BY timesDone, lastDate, score, random;", u_id, u_id, u_id, t_id)
        db._disconnect()
        return questions
    else:
        questions = db.execute("SELECT row_number() OVER (order by random()) AS random, t.topic, s.subtopic, q.q_id, q.question, q.isMultipleChoice,"
                               "(SELECT timesDONE FROM user_questions WHERE u_id = ? AND q_id = q.q_id ) AS timesDone, "
                               "(SELECT ROUND((CAST(timesRight AS REAL) / CAST(timesDone AS REAL)),2) AS score "
                               "FROM user_questions WHERE u_id = ? AND q_id = q.q_id ) AS score, "
                               "(SELECT lastDate FROM user_questions WHERE u_id = ? AND q_id = q.q_id ) as lastDate "
                               "FROM questions q INNER JOIN subtopics s USING (s_id) INNER JOIN topics t USING (t_id) "
                               "WHERE t.t_id = ? AND s.s_id IN (?) ORDER BY timesDone, lastDate, score, random;", u_id, u_id, u_id, t_id, s_id)

        return questions


def get_selected_questions(q_ids):
    questions = db.execute("SELECT t.topic, s.subtopic, q_id, question, isMultipleChoice "
                           "FROM questions INNER JOIN subtopics s USING (s_id) INNER JOIN topics t USING (t_id) "
                           "WHERE q_id IN (?);", q_ids)
    db._disconnect()
    return questions


def add_question(s_id, question, difficulty, isMultipleChoice):
    db.execute("INSERT INTO questions (s_id, question, difficulty, isMultipleChoice) values (?, ?, ?, ?)",
               s_id, question, difficulty, isMultipleChoice)
    q_id = db.execute("SELECT q_id FROM questions WHERE question = ? AND s_id = ?;", question, s_id)
    db._disconnect()
    return q_id[0]


def update_question(q_id, question, multiple):
    db.execute("BEGIN TRANSACTION;")
    db.execute("UPDATE questions SET question = ?, isMultipleChoice = ? WHERE q_id = ?;",
               question, multiple, q_id)
    changes = db.execute("SELECT changes() as changes;")
    db.execute("COMMIT;")
    db._disconnect()

    msg = f"Updated {changes[0]['changes']} question"
    return {"success": msg}


def delete_question(q_id):
    db.execute("BEGIN TRANSACTION;")
    db.execute("DELETE FROM answers WHERE q_id = ?;", q_id)
    answers = db.execute("SELECT changes() as changes;")
    db.execute("DELETE FROM questions WHERE q_id = ?;", q_id)
    questions = db.execute("SELECT changes() as changes;")
    db.execute("COMMIT;")
    db._disconnect()
    msg = f"Deleted {questions[0]['changes']} questions and {answers[0]['changes']} answers."
    if questions[0]["changes"] == 0:
        return {"error": "Nothing to delete"}
    return {"success": msg}

# ANSWERS


def get_answers(q_ids):
    answers = db.execute(
        "SELECT row_number() OVER (order by random()) AS random, q_id, a_id, answer, comment, is_true FROM answers WHERE q_id IN (?) ORDER BY q_id, random;", q_ids)
    db._disconnect()
    return answers


def add_answers(answers):
    changes = 0
    db.execute("BEGIN TRANSACTION;")
    for answer in answers:
        db.execute("INSERT INTO answers (q_id, answer, comment, is_true) values (?, ?, ?, ?);", int(
            answer["q_id"]), answer["answer"], answer["comment"], int(answer["true"]))
        change = db.execute("SELECT changes();")
        changes += change[0]["changes()"]
    db.execute("COMMIT;")
    db._disconnect()
    is_multple_choice(answers[0]["q_id"])
    return changes


def add_answer(q_id, answer, is_true, comment):
    db.execute("INSERT INTO answers (q_id, answer, is_true, comment) VALUES (?, ?, ?, ?);",
               q_id, answer, is_true, comment)
    changes = db.execute("SELECT changes();")
    db._disconnect()
    is_multple_choice(q_id)
    changes = changes[0]["changes()"]
    msg = {"success": f"Added {changes} answer"}
    if changes != 1:
        msg = {"error": "database error"}
    return msg


def update_answer(q_id, a_id, answer, is_true, comment):
    db.execute("UPDATE answers SET answer = ?, is_true = ?, comment = ? WHERE a_id = ?;",
               answer, is_true, comment, a_id)
    changes = db.execute("SELECT changes();")
    db._disconnect()
    is_multple_choice(q_id)
    changes = changes[0]["changes()"]
    msg = {"success": f"Updated {changes} answer"}
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

# TESTS


def create_test(u_id, t_id, s_id, count):
    if count == "":
        count = None
    else:
        count = get_int(count)

    questions = []
    if u_id is None or u_id == "":
        questions = get_questions(t_id, s_id)
        questions = list(questions)
        random.shuffle(questions)
        questions = questions[0:count]
    else:
        u_id = get_int(u_id)
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


def verify_test(u_id, test):
    update_db = None
    is_user = 0
    # Check user
    if not (u_id is None or u_id == ""):
        update_db = True if get_user(get_int(u_id)) == True else None
        is_user = 1

    now = dt.datetime.today().strftime("%Y-%m-%d")

    questions = []
    for q in test:
        questions.append(get_int(q))

    answers = db.execute(
        "SELECT q_id, (SELECT COUNT(*) FROM answers b WHERE a.q_id = b.q_id) as count,a_id , answer FROM answers a WHERE q_id IN (?) AND is_true = 1;", questions)
    # Update teststats only if test is finnisched
    db.execute("UPDATE teststats set testsMade = testsMade + 1, forUser = forUser + ?", is_user)
    db._disconnect()

    for q in test:
        right_answers = [a["a_id"] for a in answers if a["q_id"] == get_int(q)]
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
            exists = db.execute(
                "SELECT count(*) AS count FROM user_questions WHERE u_id = ? AND q_id = ?;", u_id, int(q))
            if len(exists) == 1 and exists[0]["count"] == 1:
                db.execute(
                    "UPDATE user_questions SET timesDone = timesDone + 1, timesRight = timesRight + ?, lastDate = ? WHERE u_id = ? AND q_id = ?;", passed, now, u_id, int(q))
                db._disconnect()
            else:
                db.execute("INSERT INTO user_questions (u_id, q_id, timesDone, timesRight, lastDate) VALUES (?, ?, ?, ?, ?);", u_id,
                           get_int(q), 1, passed, now)
                db._disconnect()


def save_test(u_id, test_name, questions):
    u_id = get_int(u_id)
    questions = ','.join(str(q) for q in questions)
    db.execute("INSERT INTO user_tests (u_id, test_name, questions) VALUES (?, ?, ?)",
               u_id, test_name, questions)
    count = db.execute("SELECT changes()")
    db._disconnect()
    if count[0]["changes()"] != 1:
        return {"error": "database error"}

    return {"success": "Your test has been saved to your user profile."}


def delete_test(u_id, ut_id):
    db.execute("DELETE FROM user_tests WHERE u_id = ? and ut_id = ?", u_id, ut_id)
    count = db.execute("SELECT changes();")
    db._disconnect()
    if count[0]["changes()"] != 1:
        return {"error": "Database error"}

    return {"success": "Test deleted"}


def get_saved_tests(u_id):
    tests = db.execute("SELECT ut_id, test_name, questions FROM user_tests WHERE u_id = ?;", u_id)
    db._disconnect()
    return tests


def get_user_test(u_id, ut_id):
    q_ids = db.execute(
        "SELECT questions FROM user_tests WHERE ut_id = ? AND u_id = ?;", ut_id, u_id)
    if len(q_ids) < 1:
        return None, None
    q_ids = q_ids[0]["questions"].split(',')
    q_ids = list(int(q) for q in q_ids)
    questions = get_selected_questions(q_ids)
    answers = get_answers(q_ids)
    db._disconnect()
    return questions, answers

# Special Feature


def is_multple_choice(q_id):
    db.execute("BEGIN TRANSACTION;")
    is_true = db.execute(
        "SELECT COUNT(*) AS count FROM answers WHERE q_id = ? AND is_true = 1", q_id)
    if is_true[0]["count"] > 1:
        db.execute("UPDATE questions SET isMultipleChoice = 1 WHERE q_id = ?;", q_id)
    else:
        db.execute("UPDATE questions SET isMultipleChoice = 0 WHERE q_id = ?;", q_id)
    db.execute("COMMIT;")
    db._disconnect()

# Tools


def add_markdown(data, *args):
    output = []
    for d in data:
        d = dict(d)
        for a in args:
            d[a] = markdown(d[a]) if d[a] is not None else ''
        output.append(d)
    return output


def get_int(i):
    if i is None:
        abort(400)
    if not isinstance(i, int):
        if isinstance(i, str):
            try:
                i = int(i)

            except ValueError:
                abort(400)
        else:
            abort(400)
    if i < 0:
        abort(400)

    return i

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
        if session.get("user_id") is None:
            return redirect("/login")
        if session["role"] not in ROLES[0]:
            abort(401)
        return f(*args, **kwargs)

    return decorated_function


def maintainer_required(f):
    """
    Decorate routes to require login.
    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        if session["role"] not in ROLES[:2]:
            abort(401)
        return f(*args, **kwargs)

    return decorated_function

def init_database():
    db.execute("BEGIN TRANSACTION;")
    db.execute("CREATE TABLE IF NOT EXISTS users (u_id INTEGER PRIMARY KEY NOT NULL DEFAULT rowid, name TEXT NOT NULL, hash TEXT NOT NULL,role TEXT NOT NULL DEFAULT 'user');")
    db.execute("CREATE TABLE IF NOT EXISTS topics (t_id INTEGER PRIMARY KEY NOT NULL DEFAULT rowid, topic TEXT NOT NULL);")
    db.execute("CREATE TABLE IF NOT EXISTS subtopics (s_id INTEGER PRIMARY KEY NOT NULL DEFAULT rowid, t_id INTEGER, subtopic TEXT NOT NULL, FOREIGN KEY (t_id) REFERENCES topics(t_id));")
    db.execute("CREATE TABLE IF NOT EXISTS questions (q_id INTEGER PRIMARY KEY NOT NULL DEFAULT rowid, s_id INTEGER NOT NULL, question TEXT NOT NULL, difficulty INTEGER DEFAULT 0, isMultipleChoice NUMERIC DEFAULT 0, FOREIGN KEY (s_id) REFERENCES subtopics(s_id));")
    db.execute("CREATE TABLE IF NOT EXISTS answers (a_id INTEGER PRIMARY KEY NOT NULL DEFAULT rowid, q_id INTEGER NOT NULL, answer TEXT NOT NULL, comment TEXT, is_true NUMERIC NOT NULL DEFAULT 0, FOREIGN KEY (q_id) REFERENCES questions(q_id));")
    db.execute("CREATE TABLE IF NOT EXISTS user_questions (u_id INTEGER NOT NULL, q_id INTEGER NOT NULL, timesDone INTEGER NOT NULL, timesRight INTEGER NOT NULL, accuracy REAL GENERATED ALWAYS AS (ROUND(CAST(timesRight AS REAL) / CAST(timesDone AS REAL),2)),lastDate TEXT);")
    db.execute("CREATE TABLE IF NOT EXISTS user_tests (ut_id INTEGER PRIMARY KEY NOT NULL DEFAULT rowid, u_id INTEGER NOT NULL, test_name TEXT NOT NULL ,questions TEXT NOT NULL, FOREIGN KEY (u_id) REFERENCES users(u_id));")
    db.execute("CREATE TABLE IF NOT EXISTS teststats (testsMade integer, forUser integer); INSERT INTO teststats VALUES(0,0);")
    db.execute("CREATE INDEX IF NOT EXISTS idx_uq ON user_questions (u_id, q_id);")
    db.execute("INSERT INTO teststats VALUES (0, 0);")
    db.execute("INSERT INTO users (name, hash, role) VALUES ('admin', ?, 'admin');", generate_password_hash('admin'))
    db.execute("COMMIT;")