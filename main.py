from flask import Flask, request, jsonify, redirect, url_for, session, render_template
from werkzeug.security import generate_password_hash, check_password_hash
import json

app = Flask(__name__)
app.secret_key = 'secret key'

#Load dotenv
from dotenv import load_dotenv
import os
load_dotenv()

ADMIN_PASS = os.getenv("ADMIN_PASS")
# Dummy user database
dummy_users = [{
        'name': 'admin',
        'username': 'admin',
        'password': generate_password_hash(ADMIN_PASS)
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

titles= [
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

# Home route to redirect to login if not logged in
@app.route('/')
def home():
    if 'username' in session:
        return jsonify({'message': 'You are logged in as ' + session['username']})
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=["GET", 'POST'])
def login():
    users = get_users()

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        for user in users:
            if username in (user["name"],user["username"]) and check_password_hash(user['password'], password):
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

#Dashboard route
@app.route('/dashboard')
@app.route("/dashboard/<int:week>")
def dashboard(week=0):
    users = get_users()

    try:
        with open('data/schedule.json') as f:
            schedule = json.load(f)
    except:
        schedule = {}

    if 'username' in session:
        name,user = get_user_and_name(users)
        print(schedule[0])
        return render_template('schedule.html', user=user, days=days, schedule=schedule[week], dates=dates, week=week, get_user=get_user)

    else:
        return redirect(url_for('login'))

def get_user(name):
    users = get_users()
    return next((user for user in users if name in (user["name"],user["username"])), None)

def get_users():
    try:
        with open('data/users.json') as f:
            users = json.load(f)
    except:
        users = dummy_users

    if not users:
        users = dummy_users
    return users


@app.route('/schedule/<int:week>', methods=["GET", "POST", "PUT"])

def schedule(week):
    try:
        with open('data/schedule.json') as f:
            schedule = json.load(f)
    except:
        schedule = [{"date":date,"title":title, "availability":[]} for date,title in zip(dates,titles)]

    users = get_users()

    if request.method in ('POST',"PUT"):
        availability = {}
        for (day,time) in request.form.items(multi=True):
            if day not in availability:
                availability[day] = []
            availability[day].append(time)
        if 'username' in session:
            current_week = schedule[week-1]
            name, user = get_user_and_name(users)
            current_week["availability"].append({name:availability})
            with open('data/schedule.json', 'w') as f:
                json.dump(schedule, f)
            
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('login'))

    return render_template('availability.html', days = list(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]),week=week, date=dates[week-1])

# Update user data
@app.route('/user', methods=["GET","POST",'PUT'])
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
        for (index,user) in enumerate(users):
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
        }
        )

        with open('data/users.json', 'w') as f:
            json.dump(users, f)

        if session["username"] != "admin":
            session["username"] = username
        return redirect(url_for('dashboard'))

    if request.method == 'GET':
        if 'username' in session:
            name,user = get_user_and_name(users)
            print(user)
            return render_template('user.html', user=user, name=name, week=0)

    return redirect(url_for('login'))


def get_user_and_name(users):
    return next(((user["name"], user["username"]) for user in users if session['username'] in (user["name"],user["username"])), None)

def set_session(user):
    session["name"] = user["name"]
    session["username"] = user["username"]

if __name__ == '__main__':
    app.run(debug=True)
