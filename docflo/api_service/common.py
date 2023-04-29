"""Contains functions commonly used across application modules.

__author__ = "Balwinder Sodhi"
__copyright__ = "Copyright 2022"
__license__ = "MIT"
__version__ = "0.1"
__status__ = "Development"
"""

import logging
import random
import re
import string
from datetime import datetime as DT
from datetime import date
from functools import wraps

from flask import current_app as app
from flask import (jsonify, session, render_template)
from flask.json import JSONEncoder

from playhouse.shortcuts import *

from models import db
from email_client import Emailer

class JSONEncoderWithDate(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, date) or isinstance(obj, DT):
                return obj.isoformat()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)

emailer = Emailer()

TS_FORMAT = "%Y%m%d_%H%M%S"

WEEK_DAY_NAMES = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']

class AppException(Exception):
    """
    Application specific exception. Its message will be passed to the clients.
    """
    pass

def lists_intersect(list_1, list_2):
    if isinstance(list_1, str):
        list_1 = list_1.split(',')
    if isinstance(list_2, str):
        list_2 = list_2.split(',')
    
    return True if set(list_1).intersection(list_2) else False

def today_str():
    return DT.now().strftime("%Y-%m-%d")


def inject_user():
    if "user" in session:
        logging.info("Found user in session: {}".format(session["user"]))
        return dict(user=session["user"])
    else:
        logging.info("User not found in session!")
        return dict()


def auth_check(_func=None, *, roles=None):
    def decor_auth(func):
        @wraps(func)
        def wrapper_auth(*args, **kwargs):
            if "user" not in session:
                msg = "Illegal access to operation. Login required."
                logging.warning(msg)
                return jsonify({"status": "ERROR", "body": msg})

            user_role = session["user"]["role"]
            if roles and user_role not in roles:
                msg = "You do not have required permissions to access."
                logging.warning(msg)
                return jsonify({"status": "ERROR", "body": msg})
            return func(*args, **kwargs)

        return wrapper_auth

    if _func is None:
        return decor_auth
    else:
        return decor_auth(_func)


def jinja2_filter_datefmt(dt, fmt=None):
    if not fmt:
        fmt = TS_FORMAT
    if isinstance(dt, str):
        dt = DT.strptime(dt, fmt)
    nat_dt = dt.replace(tzinfo=None)
    to_fmt = '%d-%m-%Y@%I:%M:%S %p'
    return nat_dt.strftime(to_fmt)


def get_ts_str():
    return DT.now().strftime(TS_FORMAT)


def parse_number(sval):
    p = "^[-+]?\d+[\./]?\d*$"
    sval = sval.strip()
    if re.search(p, sval):
        n = eval(sval)
        if isinstance(n, float):
            return round(n, 2)
        else:
            return n
    return None


def random_str(size=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=size))


def merge_json_to_model(mod, frm):
    """[summary]

    Arguments:
        mod {Model} -- peewee Model class instance
        frm {dict} -- dict from JSON object instance
    """
    # print("\n>>>>>> BEFORE: Form={0}. Model={1}".format(frm, model_to_dict(mod)))
    update_model_from_dict(mod, frm, ignore_unknown=True)
    # print("\n<<<<<<<<AFTER: Form={0}. Model={1}".format(frm, model_to_dict(mod)))


def db_connect():
    try:
        # Values are configured in config.json
        db.init(app.config['db_name'], **app.config['db_args'])
        db.connect()
    except Exception as ex:
        logging.exception("Failed to connect to DB.")


def db_close(http_resp):
    try:
        db.close()
    except Exception as ex:
        logging.exception("Failed to close DB connection.")
    return http_resp


def populate_template(template_name, data_dict):
    return render_template(template_name, **data_dict)


def current_user_name_login():
    if "user" in session:
        u = session['user']
        return "{0} {1} ({2})".format(u["first_name"], u["last_name"], u["email"])


def send_user_creation_email(to):
    try:
        body = """Hello,

Your login ID for CAMD system is your email address itself.
Please visit https://go.gtungi.in/docflo to login. 

Thanks,
CAMD"""
        subject = "User Account created"
        emailer.send_mail(to, subject, body)

    except Exception as ex:
        msg = "Error when sending user creation alert."
        logging.exception(msg)

def send_alert_email(to, about="the books"):
    try:
        body = """Hello,

There is new information available for your action in CAMD about {0}. Please login at https://go.gtungi.in/docflo to check.

Thanks,
CAMD"""
        subject = "CAMD :: New information for your action"
        emailer.send_mail(to, subject, body.format(about))

    except Exception as ex:
        msg = "Error when sending event alert."
        logging.exception(msg)
