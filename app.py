import os
import sqlite3

from flask import Flask, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3 as sql
from datetime import datetime, timedelta
from helpers import format_date, format_time
from flask_session import Session


import calendar


app = Flask(__name__)
app.secret_key = "27eduCBA09"
app.permanent_session_lifetime = timedelta(minutes=5)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

appointments = []

user_id = 8
calendar_id = 0


def create_connection(path):

    connection = None

    try:
        connection = path
        print("Connection to SQLite DB successful")

    except sql.Error as e:
        print(f"The error '{e}' occurred")

    return connection


@app.route("/", methods=["GET", "POST"])

def frontpage():
    return render_template("index.html")


@app.route("/newhops", methods=["GET", "POST"]) # tämän nimeksi oikeesti newhops


def create_hops():

    if request.method == "POST":

        title = request.form.get('title')
        add_info = request.form.get('add_info')
        max_participants = request.form.get('max_participants')
        default_hours = str(request.form.get("default_hours"))
        default_minutes = str(request.form.get("default_minutes"))
        try:
            session['default_hours'] = int(default_hours)
            session['default_minutes'] = int(default_minutes)
        except ValueError:
            return redirect("/")

        print(session['default_hours'])
        print(['default_minutes'])

        hops = {'title' : title, 'add_info': add_info, 'max_participants':max_participants, 'default_hours': session['default_hours'], 'default_minutes': session['default_minutes'] } 

        #sql_string = f"'''INSERT INTO calendar(name, owner_id, additional_info) VALUES (?,?,?)''', (title, max_participants, add_info)"
        #print(sql_string)

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO calendar(name, owner_id, additional_info) VALUES (?,?,?)''', (title, user_id, add_info))
        conn.commit()
        conn.close()


        return render_template("newappointment.html", hops=hops)

    else: 

        return render_template("newhops.html")
        
        

        # OMAT TEMPLATET TYHJÄLLE FORMILLE JA TÄYTETYLLE FORMILLE DEFAULT VALUEILLA?

    
@app.route("/new_appt", methods=["GET", "POST"])

def get_appointment():

    if request.method == "POST":

        print(f"Lets start, appointments are: {appointments}")

        year = str(request.form.get('year'))
        month = str(request.form.get('month'))
        day = str(request.form.get('day'))
        hour = str(request.form.get('hour'))
        minute = str(request.form.get('min'))

        try:
            year = int(year)
            month = int(month)
            day = int(day)
            hour = int(hour)
            minute = int(minute)
        except ValueError:
            return redirect("/new appt")                
                

        start_time = datetime(year, month, day, hour, minute)

        end_time = start_time + timedelta(hours=session['default_hours'], minutes=session['default_minutes'])

        print(start_time)
        print(end_time)

        appointment_string = f"Date: {format_date(start_time)}, starts: {format_time(start_time)}, ends: {format_time(end_time)}"

        appointment = {'start_time': start_time, 'end_time': end_time, 'string': appointment_string}

        print(appointment_string)
        message = ""
        
        if len(appointments) == 0:
            if end_time > start_time:
                appointments.append(appointment)
                new_appointment = appointment
                print("Let's add {appointment}")
                message = "Appointment added."

                conn = sqlite3.connect('database.db')
                cursor = conn.cursor()
                cursor.execute('''INSERT INTO appointment(calendar_id, starting_time, ending_time, available, description) VALUES (?,?,?,?,?)''', (calendar_id, start_time, end_time, "true", appointment_string))
                conn.commit()
                conn.close()

            else:
                message = "Invalid time"
                print("End time before start time, not valid")


        else:

            valid_time = True

            for i in range(len(appointments)):

                # if appointments start time or end time is in between 

                if appointments[i]['start_time'] < start_time < appointments[i]['end_time']:
                    print("Times are overlapping.")
                    message = "Times are overlapping"  
                    valid_time = False                  
                elif appointments[i]['start_time'] < end_time < appointments[i]['end_time']:
                    print("Times are overlapping.")
                    message = "Times are overlapping"
                    valid_time = False
                elif (appointments[i]['start_time'] == start_time) or (appointments[i]['end_time'] == end_time):
                    print("Times are overlapping")
                    message = "Times are overlapping" 
                    valid_time = False                   
                else:
                    print(f"Aikaväli {appointments[i]['start_time']} {appointments[i]['end_time']}, ehdotettu ajankohta {start_time} {end_time}")

            if valid_time == True:
                appointments.append(appointment)
                print(f"Let's add appointment: {appointment}")
                print("Appointment added.")
                message = "Appointment added."


                    

        return render_template("newappointment.html", appointments=appointments, print_appointment=appointment_string, message=message)


    else:

        create_connection(sqlite3.connect("database.db"))

        today = datetime.today()
        thisyear = today.year
        thismonth = today.month
        thisday = today.day
        year_range = []
        day_range = []
        month_range = []
        for i in range(thisyear, thisyear + 10):
            year_range.append(i)
        for i in range(0,31):
            day_range.append(i+1)
        for i in range(0, 12):
            month_range.append(i + 1)

        return render_template("newhops.html", thisyear=thisyear, year_range=year_range, month_range=month_range, day_range=day_range, today=thisday, thismonth=thismonth)



