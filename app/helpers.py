import sqlite3
from cs50 import SQL


def sql_get(statement):
    with sqlite3.connect("database.db.bak") as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute(statement)
        res = cursor.fetchall()
    return res

def get_topics():
    statement = "SELECT t_id,topic FROM topics;"
    res = sql_get(statement)
    return res

def get_users():
    statement = "SELECT u_id,name,role FROM users;"
    res = sql_get(statement)
    return res

res = get_users()
users = []
user = {}
for r in res:
    user = {r.keys()[0]: r["u_id"],r.keys()[1]: r["name"],r.keys()[2]: r["role"]}
    users.append(user)
print(users)

def get_users2():
    db = SQL("sqlite:///database.db.bak")
        users = db.execute("SELECT u_id,name,role FROM users;")
        
    return users



    


