# Load dotenv
import json
import psycopg2
from flask import Flask, request, redirect, url_for, session, render_template
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from configparser import ConfigParser
import datetime
from urllib.parse import urlparse
load_dotenv()

app = Flask(__name__)
app.secret_key = 'secret key'

conn = None


# Dummy user database
dummy_users = [{
    'name': 'admin',
    'username': 'admin',
    'password': generate_password_hash('admin')
}]

days = list(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
dates = [
    "2024-01-15",
    "2024-01-22",
    "2024-01-29",
    "2024-02-05",
    "2024-02-12",
    "2024-02-19",
    "2024-02-26",
    "2024-03-04",
    "2024-03-11",
    "2024-03-18",
    "2024-03-25",
    "2024-04-01"
]

titles = [
    "Week 1",
    "Week 2",
    "Week 3",
    "Week 4",
    "Week 5",
    "Flexible Learning Week",
    "Week 6",
    "Week 7",
    "Week 8",
    "Week 9",
    "Week 10",
    "Week 11",
]

constants = {"days": days, "dates": dates, "titles": titles}

app = Flask(__name__)
app.secret_key = 'secret key'

# Load dotenv
load_dotenv()

def load_config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)

    # get section, default to postgresql
    conStr = os.getenv("POSTGRES_URL")
    p = urlparse(conStr)
    config = {
        'dbname': "verceldb",
        'user': p.username,
        'password': p.password,
        'port': p.port,
        'host': p.hostname
    }

    return config
# Connect to the PostgreSQL database
def connect_db(config):
    try:
        # connecting to the PostgreSQL server
        with psycopg2.connect(**config) as conn:
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)


config=load_config()
conn = connect_db(config)
cur = conn.cursor()

# Home route to redirect to login if not logged in
@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=["GET", 'POST'])
def login():
    users = get_users()

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        for user in users:
            if username in (user["name"], user["username"]) and check_password_hash(user['password'], password):
                session["name"] = username
                session['username'] = username  # Store the username in the session
                return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('login'))
    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

# Dashboard route
@app.route('/dashboard')
@app.route("/dashboard/<int:week>")
def dashboard(week=-1):
    users = get_users()
    if week == -1:
        week = get_current_week()
        week -= 1
    try:
        cur.execute("SELECT schedule FROM schedule WHERE id = 1")
        schedule = cur.fetchone()[0]
        
    except:
        schedule = [{"date": date, "title": title, "availability": []} for date, title in zip(dates, titles)]
    if not schedule:
        schedule = [{"date": date, "title": title, "availability": []} for date, title in zip(dates, titles)]

    if 'username' in session:
        name, user = get_user_and_name(users)
        return render_template('schedule.html', user=user, schedule=schedule[week], constants = constants, week=week, users=users,get_user=get_user)
    else:
        return redirect(url_for('login'))

@app.route('/schedule/<int:week>', methods=["GET", "POST", "PUT"])
def schedule(week):
    users = get_users()

    try:
        cur.execute("SELECT schedule FROM schedule WHERE id = 1")
        schedule = cur.fetchone()[0]
    except:
        schedule = [{"date": date, "title": title, "availability": []} for date, title in zip(dates, titles)]

    if not schedule:
        schedule = [{"date": date, "title": title, "availability": []} for date, title in zip(dates, titles)]

    name, user = get_user_and_name(users)

    availability = find_user_availability(schedule, week)
    if request.method in ('POST', "PUT"):

        if 'username' in session:


            current_week = schedule[week]

            availability = {}
            for (day, time) in request.form.items(multi=True):
                if day not in availability:
                    availability[day] = []
                availability[day].append(time)

            for person in current_week["availability"]:
                if name in person:
                    current_week["availability"].remove(person)
                    break
            current_week["availability"].append({name: availability})
            cur.execute("UPDATE schedule SET schedule = %s WHERE id = 1", (json.dumps(schedule),))
            conn.commit()
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('login'))
    return render_template('availability.html', days=list(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]), week=week, date=dates[week], availability = availability, constants = constants)


def find_user_availability(schedule, week):
    for person in schedule[week]["availability"]:
        if session["username"] in person:
            return person[session["username"]]
    return schedule[week]["availability"]



# Update user data
@app.route('/user', methods=["GET", "POST", 'PUT'])
def user():
    # Creating a new user
    users = get_users()
    if request.method == 'POST':
        name = request.form.get('displayName')
        username = request.form.get('username')
        password = request.form.get('password')
        team = request.form.get('team')
        colour = request.form.get("colour")

        delete_user = False
        pos = 0
        for (index, user) in enumerate(users):
            if user["name"] == name:
                delete_user = True
                pos = index
        if delete_user:
            users.pop(pos)

        users.append({
            "name": name,
            "username": username,
            "password": generate_password_hash(password),
            "team": team,
            "colour": colour
        })

        cur.execute("UPDATE users SET users = %s WHERE id = 1", (json.dumps(users),))

        if session["username"] != "admin":
            session["username"] = username

        conn.commit()
        return redirect(url_for('dashboard'))

    if request.method == 'GET':
        if 'username' in session:
            name, user = get_user_and_name(users)

            return render_template('user.html', user=user, name=name, week=get_current_week(), constants = constants)

    return redirect(url_for('login'))

def get_user_and_name(users):
    return next(((user["name"], user["username"]) for user in users if session['username'] in (user["name"], user["username"])), None)

def get_users():
    cur.execute("SELECT users FROM users WHERE id = 1")
    try:
        users = cur.fetchone()[0]
    except TypeError:
        users = None
    if not users:
        users = dummy_users
    return users

def get_user(name):
    users = get_users()
    return next((user for user in users if name in (user["name"], user["username"])), None)

def get_current_week():
    today = datetime.date.today()
    for i, date in enumerate(dates):
        if today < datetime.datetime.strptime(date, "%Y-%m-%d").date():
            return i
    return -1

if __name__ == '__main__':
    if conn is not None:
        cur = conn.cursor()

        # Create tables if they don't exist
        cur.execute("CREATE TABLE IF NOT EXISTS schedule (id SERIAL PRIMARY KEY, schedule JSONB)")
        cur.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, users JSONB)")

        # Insert initial data if tables are empty
        cur.execute("SELECT COUNT(*) FROM schedule")
        if cur.fetchone()[0] == 0:
            cur.execute("INSERT INTO schedule (id, schedule) VALUES (1, %s)", (json.dumps([]),))

        cur.execute("SELECT COUNT(*) FROM users")
        if cur.fetchone()[0] == 0:
            cur.execute("INSERT INTO users (id, users) VALUES (1, %s)", (json.dumps(dummy_users),))

        conn.commit()

    app.run(debug=True, port=8080)

