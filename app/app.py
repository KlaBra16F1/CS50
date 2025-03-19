from flask import Flask, render_template, jsonify, request, redirect, flash
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import helpers as h


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/users", methods=["GET","POST"])
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

    res = h.get_users()
    return render_template("users.html", users = res)