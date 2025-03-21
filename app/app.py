from flask import Flask, render_template, jsonify, request, redirect, flash, session
from flask_session import Session
from werkzeug.security import generate_password_hash
import helpers as h

# App Setting
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
# Cookies
Session(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add-questions", methods=["GET","POST"])
def add_questions():
    if request.method == "POST":
        if request.form.get("new-topic") != "":
            new_topic = request.form.get("new-topic")
            h.add_topic(new_topic)
            flash("New topic {} created.".format(new_topic))
            return redirect("add-questions")
        if request.form.get("new-subtopic") != "":
            t_id = int(request.form.get("topic"))
            new_subtopic = request.form.get("new-subtopic")
            h.add_subtopic(t_id, new_subtopic)
            flash("New subtopic {} created.".format(new_subtopic))
            return redirect("/add-questions")
    topics = h.get_topics()
    return render_template("add-questions.html", rows_topics=topics)

@app.route("/get-subtopics")
def get_subtopics():
    t_id = request.args.get("t_id")
    subtopics = h.get_subtopics(t_id)
    return jsonify(subtopics)

@app.route("/get-questions")
def get_questions():
    t_id = request.args.get("t_id")
    s_id = request.args.get("s_id")
    questions = h.get_questions(t_id, s_id)
    return render_template("questions.html", rows = questions)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            error = "Field empty"
            flash('')
            return render_template("login.html", error=error)
        session["user_id"], session["role"], error_msg = h.login_user(username, password)
        if not session["user_id"] or not session["role"]:
            error = error_msg
            flash('')
            return render_template("login.html", error=error)
        flash("User {} successfully logged in as {}".format(username, session["role"]))
        return redirect("/users")
    return render_template("login.html")

@app.route("/users", methods=["GET","POST"])
@h.maintainer_required
def users():
    if request.method == "POST":
        print(request.form.get("delete"))
        if request.form.get("delete") != None:
            u_id = request.form.get("delete")
            name = request.form.get("name")
            h.delete_user(u_id)
            flash("User {} deleted successfully.".format(name))
            return redirect("/users")
        
        name = request.form.get("name")
        hash = generate_password_hash(request.form.get("password"))
        role = request.form.get("role")
        h.add_user(name, hash, role)
        return redirect("/users")

    users = h.get_users()
    return render_template("users.html", users = users)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("login")