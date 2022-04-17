import time
from datetime import datetime


def format_time(time_to_format):
    return time.strftime("%H:%M:%S", time.gmtime(time_to_format))


def format_date(date_to_format):
    return date_to_format.strftime("%Y-%m-%d")


def current_datetime():
    return datetime.now()


def get_date():
    return datetime.now().strftime("%Y-%m-%d")


def get_timestamp():
    return datetime.now().timestamp()


def get_formatted_time(date_time=None):
    if date_time is None:
        return datetime.now().strftime("%H:%M:%S")
    else:
        return date_time.strftime("%H:%M:%S")


def get_elapsed_time(start_time):
    return datetime.now() - start_time


# Flatten a list
def flatten_list(a_list):
    result = []
    for _list in a_list:
        result += _list
    return result
