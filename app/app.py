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
@h.maintainer_required
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
        s_id = request.form.get("subtopic")    
        question = request.form.get("question")
        difficulty = request.form.get("difficulty", None)
        isMultipleChoice = request.form.get("isMultipleChoice",0)
        q_id = h.add_question(s_id, question, difficulty, isMultipleChoice)
        flash("Question successully added. Enter Answers now.")
        return render_template("add-answers.html", q_id = q_id["q_id"], question = question)
    topics = h.get_topics()
    return render_template("add-questions.html", rows_topics=topics)

@app.route("/add-answers", methods=["GET","POST"])
@h.maintainer_required
def add_answers():
    if request.method == "POST":
        form = request.form
        answers = []
        
        print(len(form)//4+1)
        for i in range (1,len(form)//4+1):
            answer = {}
            answer["q_id"] =  form[f"answer[{i}][q_id]"]
            answer["answer"] = form[f"answer[{i}][answer]"]
            answer["comment"] = form[f"answer[{i}][comment]"]
            answer["true"] = form[f"answer[{i}][true]"]
            answers.append(answer)

        for a in answers:
            print(a["answer"])
        h.add_answers(answers)
        return redirect("/edit-questions")
        
        

    return render_template("add-answers.html")

@app.route("/edit-questions")
def edit_questions():
    topics = h.get_topics()
    return render_template("edit-questions.html", rows_topics=topics)

# Inforoutes
@app.route("/get-subtopics")
def get_subtopics():
    t_id = request.args.get("t_id")
    subtopics = h.get_subtopics(t_id)
    return jsonify(subtopics)

@app.route("/get-questions")
def get_questions():
    t_id = request.args.get("t_id")
    s_id = request.args.get("s_id")
    print(f"topic: {t_id} subtopic {s_id}")
    questions = h.get_questions(t_id, s_id)
    q_ids = [q_id["q_id"] for q_id in questions]

    answers = h.get_answers(q_ids)
    print(q_ids)
    return render_template("questions.html", questions = questions, answers = answers)

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