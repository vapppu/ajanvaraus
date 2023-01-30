import sqlite3 as sql

from datetime import datetime, timedelta
from flask import Flask, redirect, render_template, request, session, url_for, flash
from flask_session import Session
from functools import wraps
from helpers import valid_name, valid_username, valid_password, valid_email, format_timestring, valid_appointment_list
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
app.secret_key = "27eduCBA09"
app.permanent_session_lifetime = timedelta(minutes=5)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config["TEMPLATES_AUTO_RELOAD"] = True

# Create database
database = "database.db"
connection = sql.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())
connection.commit()
connection.close()


def get_connection():
    '''Connect to database and return data as a list of row objects'''
    conn = sql.connect("database.db")
    conn.row_factory = sql.Row
    return conn

def login_required(f):
    '''Make sure user has logged in'''
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            session_calendars()
            return f(*args, **kwargs)
        else:
            flash("You need to login first.")
            return redirect(url_for('login'))
        
    return wrap


def session_calendars():
    '''Define list of calendars where user has access as admin'''
    if "logged_in" in session:
        conn = get_connection()
        calendars = conn.execute('SELECT id FROM calendar WHERE owner_id = ?', (session["user"],)).fetchall()
        calendar_list = []
        for row in calendars:
            calendar_list.append(row["id"])
        session["calendars"] = calendar_list
        print(session["calendars"])


def print_appointments(rows):
    '''Create list of dictionaries from SQL query and add formatted appointment string as a new key-value pair.'''
    appointments_dict = [{k: item[k] for k in item.keys()} for item in rows]

    for dict in appointments_dict:
        dict["string"] = format_timestring(dict["starting_time"], dict["ending_time"])

    return appointments_dict


def print_available(calendar_id):
    '''Print available appointments, convert results into a list of dictionaries and add formatted appointment string as a new key-value pair'''
    conn = get_connection()
    appointments = conn.execute("SELECT * FROM appointment WHERE calendar_id = (?) AND available = 0 ORDER BY starting_time", (calendar_id, )).fetchall()
    conn.close()

    appointments_dict = [{k: item[k] for k in item.keys()} for item in appointments]

    for dict in appointments_dict:
        dict["string"] = format_timestring(dict["starting_time"], dict["ending_time"])

    return appointments_dict


def get_user():
    '''Query user data from database'''
    conn=get_connection()
    user=conn.execute("SELECT * FROM user WHERE id = (?)", (session["user"], )).fetchone()
    conn.close()
    return user


@app.route("/", methods=["GET", "POST"])

def frontpage():

    # Query and create list of all existing calendars' id numbers
    conn = get_connection()
    data = conn.execute("SELECT id FROM CALENDAR").fetchall()
    calendar_id_list = []
    for calendar in data:
        calendar_id_list.append(str(calendar["id"]))

    if request.method=="POST":
        # Get id for calendar user wants to participate in, check that calendar exists and redirect user to the calendar page
        view_id = request.form.get("calendar")
        if str(view_id) in calendar_id_list:
            return redirect(url_for("attend", calendar_id = view_id))
        else: 
            flash("Invalid calendar id!")
            return redirect("/")

    else:
        if "user" in session:
            # update list of user's calendars to session
            session_calendars()

            # query user's data and user's calendar data from database
            conn = get_connection()
            user_data = conn.execute("SELECT * FROM user WHERE id = (?)", (session["user"],)).fetchone()
            calendar_list = []
            for calendar in session["calendars"]:
                data = conn.execute("SELECT * FROM calendar WHERE id = (?)", (calendar, )).fetchone()
                calendar_list.append(data)
            conn.close()
            # for logged in users:
            return render_template("home.html", user_data=user_data, calendars = calendar_list)

        else:
            # for non-logged-in users:
            return render_template("index.html")



@app.route("/register", methods=["GET", "POST"])

def register():
    ''' Register new user '''

    if request.method == "POST":
        # get user's data from form
        firstname = request.form.get("firstname") 
        lastname = request.form.get("lastname") 
        username = request.form.get("username") 
        email = request.form.get("email") 
        password = request.form.get("password")
        password_check = request.form.get("password_check")
        hash = generate_password_hash(request.form.get("password")) 

        # validate all inputs
        valid_input = True

        if not valid_name(firstname) or not valid_name(lastname):
            flash("Name cannot begin or end with a whitespace.")
            valid_input = False

        if not valid_username(username):
            # TODO: Check that username doesn't exist already
            flash("Username cannot have whitespaces.")
            valid_input = False

        if not valid_email(email):
            flash("E-mail address not valid.")
            valid_input = False

        if not valid_password(password):
            flash("Invalid password. Check password requirements.")
            valid_input = False

        if not (password == password_check):
            flash("Passwords do not match.")
            valid_input = False

        # if some input was false, user needs to try again
        if valid_input == False:
            return render_template("register.html")

        # If all inputs were valid, insert data into database
        conn=get_connection()
        conn.execute("INSERT INTO user (username, firstname, lastname, email, password_hash) VALUES (?,?,?,?,?)", (username, firstname, lastname, email, hash))
        conn.commit()
        conn.close()

        # Redirect newly registered user to log in
        flash("Registration successful!")

        return redirect("/login")

    else:
        # Render registration form template
        return render_template("register.html")



@app.route("/login", methods=["GET", "POST"])

def login():
    ''' Log in user '''

    if request.method == "POST":

        # Get username and password from form input, query user data from database
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_connection()
        data = conn.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchall()
        conn.close()

        # If no results from database
        if len(data) == 0:
            flash('Incorrect username or password.')
            return render_template("login.html")

        # First result is the correct one?
        # TODO: What if more than 1 result? 
        else:
            user_data = data[0]

        # If password is correct, set user id to session (= user logged in)
        if check_password_hash(user_data['password_hash'], password):
            print("Correct password! Logging in.")
            session["logged_in"] = True
            session["user"] = user_data["id"] 
            print(session["user"])

        else: 
            flash("Incorrect username or password.")
            return render_template("login.html")

        # Redirect user back to index as a logged in user
        return redirect('/')

    else:
        return render_template("login.html")



@app.route("/new_calendar", methods=["GET", "POST"])
@login_required

def new_calendar():
    '''Create new calendar'''

    if request.method=="POST":
        # Request calendar data and insert into
        title = request.form.get("title")
        additional_info = request.form.get("additional_info")

        user_id = session["user"]
        print(user_id)

        # Insert new calendar into database and get back its ID
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO calendar (name, owner_id, additional_info) VALUES (?,?,?)" "RETURNING id", (title, user_id, additional_info))
        calendar_id = cursor.fetchone()["id"]                        
        conn.commit()
        conn.close()

        # Redirect to calendar's appointments page
        return redirect(url_for("appointments", calendar_id = calendar_id))

    else: 
        return render_template("new_calendar.html")


    
@app.route("/<string:calendar_id>/appointments", methods=["GET", "POST"])
@login_required

def appointments(calendar_id):
    ''' Show and edit calendar's appointments '''

    # If user doesn't have access to calendar requested in url, show error message
    if int(calendar_id) not in session["calendars"]:
        return render_template("notfound.html")

    # Get calendar's data from database
    conn = get_connection()
    calendar_data = conn.execute("SELECT * FROM calendar WHERE id = (?)", (calendar_id,)).fetchone()
    appointments_dict = []
    conn.close()
    if not 'default_start' in session:
        session['default_start'] = None

    if not 'default_duration' in session:
        session['default_duration'] = None
    
    if request.method=="POST":

        # Get starting and ending time from form input
        start = datetime.fromisoformat(request.form.get("start_time"))
        end = datetime.fromisoformat(request.form.get("end_time"))
        
        # If user gave default duration, save it to session
        if request.form.get("default_duration") != None:
            session['default_duration'] = request.form.get("default_duration")
        else:
            session['default_duration'] = None

        # Query calendar's appointments from database
        conn = get_connection()
        appointments = conn.execute("SELECT * FROM appointment WHERE calendar_id = (?)", (calendar_id, )).fetchall()
        conn.close()

        # If new appointment is valid (doesn't collide with others or itself), insert it to database
        if valid_appointment_list(appointments, start, end, None):

            conn = get_connection()
            conn.execute("INSERT INTO appointment (calendar_id, starting_time, ending_time, available) VALUES (?,?,?,?)", (calendar_id, start, end, 0))
            conn.commit()
            conn.close()

            # Set default starting time to previous ending time (next appointment starting right after previous one ended)
            session["default_start"] = end        

            flash("Appointment added!")

        return redirect("appointments")

    else:
        # Print calendar's appointments and participant names
        conn = get_connection()
        appointment_data = conn.execute("SELECT * FROM appointment LEFT OUTER JOIN answer ON appointment.id = answer.appointment_id WHERE calendar_id = (?) ORDER BY appointment.starting_time", (calendar_id, ))
        appointments_dict = print_appointments(appointment_data)

        user = get_user()

        return render_template("appointments.html", calendar_data = calendar_data, calendar_id = calendar_id, appointments_dict = appointments_dict, default_start = session['default_start'], default_duration = session['default_duration'], user=user)



@app.route("/<string:calendar_id>/appointments/edit_calendar", methods=["GET", "POST"])
@login_required

def edit_calendar(calendar_id):
    ''' Edit calendar's title and info '''

    # Make sure user has access to calendar
    if int(calendar_id) not in session["calendars"]:
        return render_template("notfound.html")

    conn = get_connection()
    calendar_data = conn.execute("SELECT * FROM calendar WHERE id = (?)", (calendar_id,)).fetchone()
    conn.close()

    if request.method=="POST":
        # Get new title and new info as user input, update them to database
        newtitle = request.form.get("title")
        new_info = request.form.get("additional_info")

        conn = get_connection()
        conn.execute("UPDATE calendar SET name = (?), additional_info = (?) WHERE id = (?);", (newtitle, new_info, calendar_id))
        conn.commit()
        conn.close()

        flash("Changes saved!")
        return redirect(url_for("edit_calendar", calendar_id=calendar_id))
    else:
        return render_template("edit_calendar.html", calendar_id = calendar_id, calendar_data = calendar_data)



@app.route("/<string:calendar_id>/appointments/delete_calendar", methods=["GET"])
@login_required

def delete_calendar(calendar_id):
    ''' Deletes calendar '''

    # Make sure user has access to calendar
    if int(calendar_id) not in session["calendars"]:
        return render_template("notfound.html")

    # Delete calendar from database
    # TODO: What if calendar doesn't exist?
    conn = get_connection()
    conn.execute("DELETE FROM calendar WHERE id = (?)", (calendar_id, ))
    conn.commit()
    conn.close()
    flash("Calendar deleted.")
    return redirect("/")



@app.route("/about", methods=["GET"])

def about_us():
    '''Show about us page'''
    return render_template("about.html")



@app.route("/attend/<string:calendar_id>", methods=["GET", "POST"])

def attend(calendar_id):
    '''Page for other users to book their appointment'''

    # Print available appointments
    appointments_dict = print_available(calendar_id)        

    # Get calendar info from database
    conn = get_connection()
    calendar_data = conn.execute("SELECT * FROM calendar WHERE id = (?)", (calendar_id, )).fetchone()

    # If calendar was found, get user's data from database as well
    if calendar_data != None:
        user_data = conn.execute("SELECT id, firstname, lastname, email FROM user WHERE id = (?)", (calendar_data["owner_id"], )).fetchone()
        conn.close()
    else:
        conn.close()
        return render_template("notfound.html")

    # Ask participant's name and e-mail, get appointment id from radio button
    if request.method=="POST":
        name = request.form.get("name")
        email = request.form.get("email")
        appointment = request.form.get("appointment")

        # If user didn't select any appointment, flash message and redirect to same page.
        if appointment == None:
            flash("Please select appointment.")
            return redirect(url_for("attend", calendar_id = calendar_id))

        # Get selected appointment's data from database and make sure it is available
        conn=get_connection()
        data = conn.execute("SELECT available FROM appointment WHERE id = (?)", (appointment, )).fetchone()
        available = data["available"]

        # If appointment is available, insert data into answer table in database.
        if available == 0:
            conn.execute("UPDATE appointment SET available = 1 WHERE id = (?)", (appointment, ))
            conn.execute("INSERT INTO answer (appointment_id, timestamp, participant_name, participant_email) VALUES (?,CURRENT_TIMESTAMP,?, ?)", (appointment, name, email))
            conn.commit()
            conn.close()
            appointment_string = appointments_dict[available]["string"]
            return render_template("thankyou.html", name=name, booked_appointment=appointment_string, user_data=user_data, calendar_data=calendar_data)

        else:
            flash("Appointment is not available.")
            return redirect(url_for("attend", calendar_id=calendar_id))

    else:
        return render_template("attend.html", appointments_dict = appointments_dict, calendar_id = calendar_id, calendar_data = calendar_data, user_data = user_data)



@app.route("/logout")
def logout():
    '''Log user out'''
    print(f'logging out user {session["user"]}')
    session.clear()
    return redirect("/")


@app.route("/<string:calendar_id>/<string:appointment_id>/delete", methods=["GET", "POST"])
@login_required
def delete_appointment(appointment_id, calendar_id):
    '''Deletes appointment and returns back to appointments page'''

    #Make sure user has access to calendar
    if int(calendar_id) not in session["calendars"]:
        return render_template("notfound.html")

    conn = get_connection()
    conn.execute("DELETE FROM appointment WHERE id = (?)", (appointment_id, ))
    flash("Appointment deleted.")
    conn.commit()
    conn.close()

    return redirect(url_for("appointments", calendar_id = calendar_id))



@app.route("/<string:calendar_id>/<string:appointment_id>/edit", methods=["GET", "POST"])
@login_required
def edit_appointment(calendar_id, appointment_id):
    '''Edit appointment's starting and ending time'''

    # Make sure user has access to calendar
    if int(calendar_id) not in session["calendars"]:
        return render_template("notfound.html")

    conn = get_connection()
    appointment = conn.execute("SELECT * FROM appointment WHERE id = (?)", (appointment_id, )).fetchone()
    appointments = conn.execute("SELECT * FROM appointment WHERE calendar_id = (?)", (calendar_id, )).fetchall()
    conn.close()

    # Get appointment's index calendar's list of appointments (needed for validation checking)
    index = appointments.index(appointment)
    print("Index is ", index)

    if request.method =="POST":
        # Get new starting and ending times as form input
        new_starting_time = datetime.fromisoformat(request.form.get("starting_time"))
        new_ending_time = datetime.fromisoformat(request.form.get("ending_time"))

        # Check appointment validity (doesn't collide with itself or other appointments), and update database
        if valid_appointment_list(appointments, new_starting_time, new_ending_time, index):
        
            conn = get_connection()
            conn.execute("UPDATE appointment SET starting_time = (?), ending_time = (?) WHERE id = (?)", (new_starting_time, new_ending_time, appointment_id))
            conn.commit()
            conn.close

            flash("Appointment edits saved")

        return redirect(url_for("appointments", calendar_id=calendar_id))

    return render_template("edit_appointment.html", calendar_id = calendar_id, appointment=appointment)