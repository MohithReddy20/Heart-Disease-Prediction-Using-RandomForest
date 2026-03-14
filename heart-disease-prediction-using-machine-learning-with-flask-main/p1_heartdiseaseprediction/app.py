from flask import Flask, render_template, request, redirect, session, url_for
from sqlite3 import connect
from flask_mail import Mail
from random import randrange
from werkzeug.security import generate_password_hash, check_password_hash
import pickle
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ---------------- MAIL CONFIG ----------------
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USERNAME"] = "your_email@gmail.com"
app.config["MAIL_PASSWORD"] = "your_app_password"
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False

mail = Mail(app)

# ---------------- LOAD MODEL ONCE ----------------
with open("heartdiseaseprediction.model", "rb") as f:
    model = pickle.load(f)

print("Model loaded. Classes:", model.classes_)

# ---------------- HOME ----------------
@app.route("/")
def home():
    if 'username' in session:
        return render_template("home.html", name=session['username'])
    return redirect(url_for('login'))


# ---------------- FIND PAGE ----------------
@app.route("/find")
def find():
    if 'username' in session:
        return render_template("find.html", name=session['username'])
    return redirect(url_for('login'))


# ---------------- PREDICTION ----------------
@app.route("/check", methods=["POST"])
def check():
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        age = float(request.form["age"])
        cp = int(request.form["r1"])
        BP = float(request.form["BP"])
        CH = float(request.form["CH"])
        maxhr = float(request.form["maxhr"])
        STD = float(request.form["STD"])
        fluro = float(request.form["fluro"])
        Th = float(request.form["Th"])

        # Use DataFrame to avoid sklearn warning
        features = pd.DataFrame([{
            "Age": age,
            "Chest pain type": cp,
            "BP": BP,
            "Cholesterol": CH,
            "Max HR": maxhr,
            "ST depression": STD,
            "Number of vessels fluro": fluro,
            "Thallium": Th
        }])

        prediction = model.predict(features)[0]
        probability = model.predict_proba(features)[0][1]
        print("Features:", features)
        print("Prediction:", prediction)
        print("Probability:", probability)


        return render_template(
            "find.html",
            msg=prediction,
            probability=round(probability * 100, 2),
            name=session['username']
        )

    except Exception as e:
        return render_template(
            "find.html",
            msg="Error in prediction: " + str(e),
            name=session['username']
        )


# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        un = request.form["un"]
        em = request.form["em"]

        # Generate 6 digit password
        pw = "".join(str(randrange(10)) for _ in range(6))
        hashed_pw = generate_password_hash(pw)

        try:
            with connect("monicaheart.db") as con:
                cursor = con.cursor()
                cursor.execute(
                    "INSERT INTO user VALUES (?, ?)",
                    (un, hashed_pw)
                )
                con.commit()

            print("--------------------------------------------------")
            print("GENERATED PASSWORD:", pw)
            print("--------------------------------------------------")

            return render_template(
                "login.html",
                msg="Account created successfully. Check terminal for password."
            )

        except Exception:
            return render_template(
                "signup.html",
                msg="User already exists."
            )

    return render_template("signup.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        un = request.form["un"]
        pw = request.form["pw"]

        try:
            with connect("monicaheart.db") as con:
                cursor = con.cursor()
                cursor.execute(
                    "SELECT password FROM user WHERE username=?",
                    (un,)
                )
                data = cursor.fetchone()

            if data and check_password_hash(data[0], pw):
                session['username'] = un
                return redirect(url_for('home'))
            else:
                return render_template("login.html", msg="Invalid login")

        except Exception as e:
            return render_template("login.html", msg="Issue: " + str(e))

    return render_template("login.html")


# ---------------- FORGOT PASSWORD ----------------
@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        un = request.form["un"]
        em = request.form["em"]

        try:
            with connect("monicaheart.db") as con:
                cursor = con.cursor()
                cursor.execute(
                    "SELECT * FROM user WHERE username=?",
                    (un,)
                )
                data = cursor.fetchone()

            if not data:
                return render_template("forgot.html", msg="Invalid username")

            # Generate new password
            new_pw = "".join(str(randrange(10)) for _ in range(6))
            hashed_pw = generate_password_hash(new_pw)

            with connect("monicaheart.db") as con:
                cursor = con.cursor()
                cursor.execute(
                    "UPDATE user SET password=? WHERE username=?",
                    (hashed_pw, un)
                )
                con.commit()

            print("--------------------------------------------------")
            print("NEW PASSWORD:", new_pw)
            print("--------------------------------------------------")

            return render_template(
                "login.html",
                msg="New password generated. Check terminal."
            )

        except Exception as e:
            return render_template("forgot.html", msg="Issue: " + str(e))

    return render_template("forgot.html")


# ---------------- LOGOUT ----------------
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)
