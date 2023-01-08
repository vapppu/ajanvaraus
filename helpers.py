from datetime import datetime, timedelta
from flask import redirect, render_template, request, session
import calendar


def format_date(datetime_object):

    date_style = "%Y/%m/%d"
    date_format = datetime_object.strftime(date_style)
    return date_format


def format_time(datetime_object):
    time_style = "%H:%M"
    time_format = datetime_object.strftime(time_style)
    return time_format



