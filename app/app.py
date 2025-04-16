from flask import Flask, render_template, jsonify, request, redirect, flash, session, abort
from flask_session import Session
from werkzeug.security import generate_password_hash
import werkzeug.exceptions
from markdown import markdown
import helpers as h

# App Setting
app = Flask(__name__)
app.config.from_prefixed_env()
app.config["SECRET_KEY"]
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
# Cookies
Session(app)


@app.route("/")
def index():
    return render_template("index.html")

# Questions


@app.route("/add-questions", methods=["GET", "POST"])
@h.maintainer_required
def add_questions():
    if request.method == "POST":
        if request.form.get("new-topic") != "":
            new_topic = request.form.get("new-topic")
            msg = h.add_topic(new_topic)
            if msg.get("error"):
                flash(msg.get("error"), "Error")
                return redirect("/add-questions")
            else:
                flash(msg.get("success"), "Success")
                return redirect("/add-questions")

        if request.form.get("new-subtopic") != "":
            if not request.form.get("topic"):
                error = "Select a topic first to create a subtopic."
                flash(error, "Error")
                return redirect("/add-questions")
            t_id = h.get_int(request.form.get("topic"))
            new_subtopic = request.form.get("new-subtopic", "")
            msg = h.add_subtopic(t_id, new_subtopic)
            if msg.get("error"):
                flash(msg.get("error"), "Error")
                return redirect("/add-questions")
            else:
                flash(msg.get("success"), "Success")
                return redirect("/add-questions")

        if request.form.get("subtopic") == "":
            flash("You must select a subtopic before adding a questions", "Error")
            return redirect("/add-questions")
        s_id = h.get_int(request.form.get("subtopic", None))
        question = request.form.get("question", None)
        difficulty = request.form.get("difficulty", None)
        isMultipleChoice = request.form.get("isMultipleChoice", 0)
        if question == "":
            flash("Question can't be empty", "Error")
            return redirect("/add-questions")

        q_id = h.add_question(s_id, question, difficulty, isMultipleChoice)
        question = markdown(question)

        flash("Question successully added. Enter Answers now.")
        return render_template("add-answers.html", q_id=q_id["q_id"], question=question)

    topics = h.get_topics()
    return render_template("add-questions.html", rows_topics=topics)


@app.route("/edit-questions")
@h.maintainer_required
def edit_questions():
    if request.args.get("delete"):
        q_id = h.get_int(request.args.get("delete"))
        msg = h.delete_question(q_id)
        return msg
    if request.args.get("delTopicSubtopic"):
        if request.args.get("delTopicSubtopic") == "t_id":
            t_id = h.get_int(request.args.get("id"))
            msg = h.delete_topic(t_id)

            return msg

        elif request.args.get("delTopicSubtopic") == "s_id":
            s_id = request.args.get("id")
            msg = h.delete_subtopic(s_id)

        else:
            abort(400)

    if request.args.get("update"):
        q_id = h.get_int(request.args.get("update"))
        question = request.args.get("question", None)
        multiple = request.args.get("multiple", None)
        if question == "":
            return {"error": "Question can't be empty."}
        msg = h.update_question(q_id, question, multiple)
        return msg

    topics = h.get_topics()
    return render_template("edit-questions.html", rows_topics=topics)

# Answers


@app.route("/add-answers", methods=["GET", "POST"])
@h.maintainer_required
def add_answers():
    if request.method == "POST":
        form = request.form
        # Extract multiple answers from form
        answers = []
        for i in range(1, len(form)//4+1):
            answer = {}
            answer["q_id"] = h.get_int(form[f"answer[{i}][q_id]"])
            answer["answer"] = form[f"answer[{i}][answer]"]
            if answer["answer"] == "":
                continue
            answer["comment"] = form[f"answer[{i}][comment]"]
            answer["true"] = h.get_int(form[f"answer[{i}][true]"])
            answers.append(answer)

        changes = h.add_answers(answers)
        flash(f"Added {changes} questions.", "Success")
        return redirect("/add-questions")

    if request.args.get("q_id"):
        q_id = h.get_int(request.args.get("q_id", None))
        answer = request.args.get("answer", "")
        is_true = request.args.get("is_true", 0)
        comment = request.args.get("comment", "")
        if answer == "":
            return {"error": "Answer can't be empty."}
        msg = h.add_answer(q_id, answer, is_true, comment)
        return msg
    else:
        return redirect("/add-questions")


@app.route("/edit-answers", methods=["GET", "POST"])
@h.maintainer_required
def edit_answers():

    if request.args.get("question"):
        q_id = []
        q_id.append(h.get_int(request.args.get("question")))
        question = h.get_selected_questions(q_id)
        if len(question) < 1:
            abort(400)
        question = h.add_markdown(question, "question")
        return render_template("edit-answers.html", question=question[0])

    if request.args.get("update_answer"):
        a_id = h.get_int(request.args.get("update_answer"))
        answer = request.args.get("answer", "")
        is_true = request.args.get("is_true")
        comment = request.args.get("comment")
        q_id = h.get_int(request.args.get("q_id"))
        if answer == "":
            return {"error": "Answer can't be empty"}
        msg = h.update_answer(q_id, a_id, answer, is_true, comment)
        return msg

    if request.args.get("delete"):
        a_id = h.get_int(request.args.get("delete"))
        q_id = h.get_int(request.args.get("q-id"))
        msg = h.delete_answer(a_id, q_id)
        return msg
    return redirect("/edit-questions")


# Tests

@app.route("/make-test", methods=["GET", "POST"])
def make_test():

    session["q_order"] = ""
    session["a_order"] = ""
    if request.method == "POST":
        t_id = request.form.get("topic")
        s_id = request.form.get("subtopic")
        count = request.form.get("count", 0)

        if not session.get("user_id"):
            u_id = None
        else:
            u_id = session["user_id"]
        # Extract subtopics
        if s_id != "":
            s_id = s_id[1:-1]
            s_id = s_id.split(',')
            s_id = list(h.get_int(s) for s in s_id)

        questions, answers = h.create_test(u_id, t_id, s_id, count)
        questions = h.add_markdown(questions, "question")
        answers = h.add_markdown(answers, "answer", "comment")
        session["q_order"] = [q["q_id"] for q in questions]
        session["a_order"] = [a["a_id"] for a in answers]
        return render_template("test.html", questions=questions, answers=answers)
    topics = h.get_topics()

    if request.args.get("test"):
        if session.get("user_id") is None:
            abort(400)
        ut_id = h.get_int(request.args.get("test"))
        questions, answers = h.get_user_test(session["user_id"], ut_id)
        if questions is None or answers is None:
            abort(400)
        questions = h.add_markdown(questions, "question")
        answers = h.add_markdown(answers, "answer", "comment")
        session["q_order"] = [q["q_id"] for q in questions]
        session["a_order"] = [a["a_id"] for a in answers]
        return render_template("test.html", questions=questions, answers=answers)

    return render_template("make-test.html", rows_topics=topics)


@app.route("/get-results", methods=["POST"])
def get_results():
    test = {}
    # extract questions/answers dict

    for r in request.form:
        if r.__contains__("."):
            rs = r.split(".")
            if rs[0] == "question":
                test[rs[1]] = []
            else:
                test[rs[0]].append(h.get_int(rs[1]))
        else:
            test[r].append(h.get_int(request.form.get(r)))

    # send answers to users table
    u_id = None if session is None else session.get("user_id")
    h.verify_test(u_id, test)
    questions = h.get_questions_result(session["q_order"])
    questions = h.add_markdown(questions, "question")
    answers = h.get_answers(session["q_order"])
    answers = h.add_markdown(answers, "answer", "comment")
    # Send questions in same random order like make_test
    questions_ordered = []
    for q in session["q_order"]:
        for question in questions:
            if question["q_id"] == h.get_int(q):
                questions_ordered.append(question)
    # Send answers in same random order like make_test
    answers_ordered = []
    for a in session["a_order"]:
        for answer in answers:
            if answer["a_id"] == h.get_int(a):
                answers_ordered.append(answer)
    return render_template("results.html", questions=questions_ordered, answers=answers_ordered, test=test)


@app.route("/save-test")
@h.login_required
def save_test():
    if request.args.get("save") and h.get_int(request.args.get("save")) == session["user_id"]:

        questions = session["q_order"]
        msg = h.save_test(session["user_id"], str(request.args.get("name")), questions)
        return msg

    return redirect("/")


@app.route("/delete-test")
@h.login_required
def delete_test():
    if request.args.get("ut_id"):
        ut_id = h.get_int(request.args.get("ut_id", None))
        msg = h.delete_test(session["user_id"], ut_id)
        return msg
    abort(400)

# Inforoutes


@app.route("/get-subtopics")
def get_subtopics():
    if request.args.get("t_id"):
        t_id = request.args.get("t_id")
        if t_id != "":
            t_id = h.get_int(t_id)
        subtopics = h.get_subtopics(t_id)
        return jsonify(subtopics)
    return {"empty": 200}


@app.route("/get-questions")
@h.maintainer_required
def get_questions():
    t_id = request.args.get("t_id")
    if t_id != "":
        t_id = h.get_int(t_id)
    s_id = request.args.get("s_id")
    if s_id != "":
        s_id = h.get_int(s_id)
    questions = h.get_questions(t_id, s_id)
    questions = h.add_markdown(questions, "question")
    q_ids = [q_id["q_id"] for q_id in questions]
    answers = h.get_answers(q_ids)

    # Markdown
    answers = h.add_markdown(answers, "answer", "comment")
    return render_template("modules/questions.html", questions=questions, answers=answers)


@app.route("/get-answers")
@h.maintainer_required
def get_answers():
    q_id = h.get_int(request.args.get("q_id"))
    answers = h.get_answers(q_id)
    answers = sorted(answers, key=lambda x: x["a_id"])
    answers = h.add_markdown(answers, "answer", "comment")
    return render_template("modules/answers.html", answers=answers)

# Statistics


@app.route('/statistics')
@h.maintainer_required
def stats():
    stats = h.get_sitestats()
    return render_template("statistics.html", stats=stats)


@app.route("/diagram-api")
@h.maintainer_required
def diagram_api():
    if request.args.get("topic"):
        data = h.topics_diagramm()
        print(data)
        if len(data) < 1:
            return [{"percent": 0, "topic": ""}]
        return jsonify(data)
    if request.args.get("users"):
        data = h.userTopics_diagram()
        if len(data) < 1:
            return [{"percent": 0, "topic": ""}]
        return jsonify(data)

    abort(400)


@app.route("/reset-site-statistics", methods=["POST"])
@h.admin_required
def delete_site_stats():
    h.reset_site_stats()
    flash("Site statistics have been reset.")
    return redirect("/statistics")

# Users


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect("/")
    if request.method == "POST":
        if not (request.form.get("username") and request.form.get("password") and request.form.get("confirm")):
            abort(400)
        else:
            msg = h.register_user(request.form.get('username'), request.form.get(
                "password"), request.form.get("confirm"))

            if msg.get("error"):
                flash(msg.get("error"), "Error")
                return redirect("/register")
            else:
                flash(msg.get("success"), "Success")
                return redirect("/login")

    if request.args.get("username"):
        username = request.args.get("username")
        ok = 'ok' if h.check_username(username) == 0 else 'error'
        return jsonify(ok)

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            flash("User not found or password incorrect", "Error")
            return redirect("/login")
        session["user_name"], session["user_id"], session["role"], error_msg = h.login_user(
            username, password)

        if not session["user_id"] or not session["role"]:
            flash(error_msg, "Error")
            return redirect("/login")
        flash("User {} successfully logged in as {}".format(username, session["role"]), "Success")
        return redirect("/profile")
    return render_template("login.html")


@app.route("/users", methods=["GET", "POST"])
@h.admin_required
def users():
    if request.method == "POST":
        if request.form.get("delete") != None:
            u_id = h.get_int(request.form.get("delete"))
            name = request.form.get("name")
            msg = h.delete_user(u_id)
            if msg.get("error"):
                flash(msg.get("error"), "Error")
            else:
                flash(msg.get("success"), "Success")
            return redirect("/users")

        if request.form.get("change-role") != None:
            msg = h.change_role(request.form.get("change-role"), request.form.get("role"))

            if msg.get("error"):
                flash(msg.get("error"), "Error")
            else:
                flash(msg.get("success"), "Success")
            return redirect("/users")

        name = request.form.get("name")
        hash = generate_password_hash(request.form.get("password"))
        role = request.form.get("role")
        msg = h.add_user(name, hash, role)
        if msg.get("error"):
            flash(msg.get("error"), "Error")
        else:
            flash(msg.get("success"), "Success")
        return redirect("/users")

    users = h.get_users()
    return render_template("users.html", users=users, roles=h.ROLES)


@app.route("/profile", methods=["GET", "POST"])
@h.login_required
def profile():
    u_id = session["user_id"]
    if request.method == "POST":
        if h.get_int(request.form.get("deleteStats")) == session["user_id"]:
            msg = h.delete_stats(u_id)
            if msg.get("error"):
                flash(msg.get("error"), "Error")
            else:
                flash(msg.get("success"), "Success")

            return redirect("/profile")

    if request.args.get("t_id"):
        t_id = h.get_int(request.args.get("t_id"))
        subtopics = h.get_userstats_details(t_id, u_id)
        return render_template("modules/user-stats-subtopics.html", subtopics=subtopics)

    tests = h.get_saved_tests(u_id)
    stats = h.get_userstats(u_id)
    return render_template("profile.html", tests=tests, stats=stats)


@app.route("/change-password", methods=["POST"])
@h.login_required
def change_password():
    old_pw = request.form.get("old-pw", None)
    pw = request.form.get("password", None)
    confirm = request.form.get("confirm", None)
    if old_pw and pw and confirm:
        msg = h.change_password(session["user_id"], old_pw, pw, confirm)
        if msg.get("error"):
            flash(msg.get("error"), "Error")
        else:
            flash(msg.get("success"), "Success")
    else:
        flash("Something is wrong with your input", "Error")

    return redirect("/profile")


@app.route("/delete-account", methods=["POST"])
@h.login_required
def delete_account():
    password = request.form.get("password", None)

    if password:

        msg = h.delete_account(session["user_id"], password)
        if msg.get("error"):
            flash(msg.get("error"), "Error")
            return redirect("/profile")
        else:
            flash(msg.get("success"), "Success")
            return redirect("/logout")


@app.route("/logout")
@h.login_required
def logout():
    session.clear()
    return redirect("login")

# ERRORS


@app.errorhandler(werkzeug.exceptions.BadRequest)
def handle_bad_request(e):
    err = str(e).split(":")
    return render_template("error.html", error=err), 400


@app.errorhandler(werkzeug.exceptions.Unauthorized)
def handle_unauthorized(e):
    err = str(e).split(":")
    return render_template("error.html", error=err), 401


@app.errorhandler(werkzeug.exceptions.NotFound)
def not_found(e):
    err = str(e).split(":")
    return render_template("error.html", error=err), 404


@app.errorhandler(werkzeug.exceptions.MethodNotAllowed)
def handle_method_not_allowed(e):
    err = str(e).split(":")
    return render_template("error.html", error=err), 405


@app.errorhandler(500)
def server_error(e):
    err = str(e).split(":")
    return render_template("error.html", error=err), 500
