from flask import Flask, render_template, jsonify
from flask_session import Session
import helpers as h


app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/users")
def users():
    res = h.get_users2()
    # users = []
    # user = {}
    # for r in res:
    #     user = {r.keys()[0]: r["u_id"],r.keys()[1]: r["name"],r.keys()[2]: r["role"]}
    #     users.append(user)
    return jsonify(res)