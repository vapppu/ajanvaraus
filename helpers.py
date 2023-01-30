import re

from datetime import datetime
from flask import flash





def format_datetime(obj):
    '''Formats datetime object to string representation'''
    formatted = obj.strftime('%a %d %b %Y %H:%M')
    return formatted


def format_timestring(string1, string2):
    # Formats time frame between two datetime objects into string representation
    try:
        time1 = datetime.strptime(string1, "%Y-%m-%d %H:%M:%S")
        time2 = datetime.strptime(string2, "%Y-%m-%d %H:%M:%S")

        if time1.date() == time2.date():
            formatted = (format_datetime(time1)) + " - " + (time2.strftime('%H:%M'))
        else:
            formatted = (format_datetime(time1)) + " - " + format_datetime(time2)
        return formatted

    except:
        print("Time conversion wasn't successful.")



def valid_name(text):
    '''Check sure name doesn't start or end with whitespace'''
    if (text[0] == " " or text[-1] == " "):
        return False  
    else:
        return True


def valid_username(text):
    '''Check username doesn't have whitespaces'''
    for char in text:
        if char == " ":
            return False
    return True


def valid_password(text):
    '''Check password has upper and lowercase letters, numbers and special characters'''
    length = False
    upper = False
    lower = False
    digit = False
    special = False
    if len(text) >= 8:
        length = True
    for char in text:
        if char.isupper():
            upper = True
        elif char.islower():
            lower = True
        elif char.isdigit():
            digit = True
        else:
            special = True

    if (length and upper and lower and digit and special):
        return True
    else:
        return False


def valid_email(text):
    '''Check e-mail address is valid'''
    if re.fullmatch((r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'), text) != None:
        return True
    else:
        return False


def valid_appointment_list(dict, time1, time2, index):
    '''Check time frame doesn't collide with itself or with other appointments in a list of
    appointment dictionaries. If an existing appointment is being edited, we need to know appointment's
    index in the list of appointment dictionaries in order to skip it when comparing appointment
    to existing appointments'''

    # Make sure starting time is before ending time
    if time1 >= time2:
        flash("Changes not saved: appointment cannot end before its starting time!")
        return False

    # Check that starting time and ending time are is not inside an existing appointment.
    # Allow an appointment to begin in the same minute as another one ends.
    for i in range(len(dict)):
        if i == index:
            print(index, "=", i)
            continue
        elif to_datetime(dict[i]["starting_time"]) <= time1 < to_datetime(dict[i]["ending_time"]):
            flash("Changes not saved: appointment cannot collide with other appointments!")
            return False
        elif to_datetime(dict[i]["starting_time"]) < time2 <= to_datetime(dict[i]["ending_time"]):
            flash("Changes not saved: appointment cannot collide with other appointments!")            
            return False
        else:
            continue
        
    return True


def to_datetime(string):
    '''Convert datetime string (from database query) into datetime object which can be
    compared to others.'''
    return (datetime.strptime(string, "%Y-%m-%d %H:%M:%S"))



