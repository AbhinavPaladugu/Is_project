from flask import Flask, render_template, request, flash, redirect
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

DATABASE = "paladugudb.db"


def init_db():
    """Create the database and users table."""
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()


@app.route("/")
def index():
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Registration page to add users."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            flash("Registration successful!", "success")
        except sqlite3.IntegrityError:
            flash("Username already exists. Please choose another.", "danger")
        finally:
            conn.close()

        return redirect("/register")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Login page with SQL injection vulnerability."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Vulnerable query
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            user = cursor.fetchone()
            if user:
                flash("Login successful! Welcome back!", "success")
            else:
                flash("Invalid credentials or SQL injection attempt detected.", "danger")
        except sqlite3.OperationalError as e:
            flash(f"Database error: {e}", "danger")
        finally:
            conn.close()

        return redirect("/login")

    return render_template("login.html")


@app.route("/demo")
def demo():
    """SQL injection demonstration instructions."""
    return render_template("demo.html")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
