"""Common functions used by various view modules.

__author__ = "Balwinder Sodhi"
__copyright__ = "Copyright 2022"
__license__ = "MIT"
__version__ = "0.1"
__status__ = "Development"
"""

import json
import os
from pathlib import Path

import toml
from flask.blueprints import Blueprint

from common import *
from models import *

logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

# For pagination
PAGE_SIZE = 25
STATUS_TRAN = ["A2EDIT-EDITDONE", "IMPORTED-A2CORD", 
                "EDITDONE-ACCEPTED", "EDITDONE-R2EDIT",
                "DRAFT-EDITDONE"]
STATUS_MAP = {
        "MED": ["DRAFT", "A2EDIT", "R2EDIT"],
        "CCR": ["DRAFT", "A2EDIT", "R2EDIT"],
        "COR": ["DRAFT", "A2CORD", "A2EDIT", "R2EDIT", "EDITDONE"],
        "SUP": ["DRAFT", "A2CORD", "A2EDIT", "R2EDIT", "EDITDONE", 
                "ACCEPTED", "IMPORTED"], 
        "MGR": ["DRAFT", "A2CORD", "A2EDIT", "R2EDIT", "EDITDONE",
                "ACCEPTED", "IMPORTED"]
    }

vbp = Blueprint('bp', __name__, template_folder='templates')

def log_error(ex, msg):
    msg = str(ex) if isinstance(ex, (AppException, IntegrityError)) else msg
    logging.exception(msg)
    return msg


def get_sql(sql_id):
    """
    docstring
    """
    sql_dict = toml.load("queries.toml")
    return sql_dict[sql_id]


def session_user():
    if "user" in session:
        return session['user']


def logged_in_user():
    if "user" in session:
        u = session['user']
        return User.get(User.email == u["email"])


def current_login_id():
    if "user" in session:
        u = session['user']
        return u["email"]


def current_role():
    if "user" in session:
        u = session['user']
        return u["role"]


def is_user_in_role(role):
    """Checks whether the currently logged in user has at least
    one of the given role(s).

    The supplied argument can be a single role code string, e.g., "STU",
    or it can be a list of such codes, e.g., ["HOD", "ACA"]
    or even a comma-separated list of role codes such as:
    "HOD,ACA,DEA".
    The role codes must be unique strings.
    
    Args:
        role (str or list of str): Role code or a list of role codes.

    Returns:
        bool: True if the user has any one of the role(s) supplied, else False
    """
    if "user" in session:
        u = session['user']
        return u["role"] in role
    else:
        return False


def current_user():
    if "user" in session:
        u = session['user']
        nav = make_nav(u["role"])
        return ok_json({"user": u, "nav": nav})
    else:
        return error_json("User not logged in.")


def static_data_dict():
    with open(os.path.join(app.root_path, "static_data.json"), "r") as str_json:
        sd = json.load(str_json)        
        return sd


def get_static_data_item(item_key):
    sd = static_data_dict()
    return sd[item_key]


def get_static_data_item_label(item_code, items_map):
    long_label = item_code
    for y in items_map:
        ct = item_code
        if ct == y["id"]:
            long_label = y["value"]
            break

    return long_label


def save_entity(obj):
    obj.ins_by = logged_in_user().email
    obj.upd_ts = DT.now()
    obj.ins_ts = DT.now()
    return obj.save()


def update_entity(entity, obj, exclude=[]):
    txn_no = int(obj.txn_no or 0)
    obj.txn_no = 1 + txn_no
    obj.upd_ts = DT.now()
    obj.upd_by = logged_in_user().email
    # Don't update the insert timestamp
    exclude.append(getattr(entity, "ins_ts"))
    exclude.append(getattr(entity, "ins_by"))
    mdict = model_to_dict(obj, recurse=False, exclude=exclude)
    return entity.update(mdict).where(
        (entity.txn_no == obj.txn_no - 1) &
        (entity.id == obj.id)).execute()


def ok_json(obj):
    return jsonify({"status": "OK", "body": obj})


def error_json(obj):
    return jsonify({"status": "ERROR", "body": obj})


def get_upload_folder(sub_dir=None):
    # Ensure that the uploads folder for this user exists
    uf = app.config['upload_folder']
    if sub_dir:
        uf = os.path.join(uf, sub_dir)
    Path(uf).mkdir(parents=True, exist_ok=True)
    return uf


def get_upload_folder_for_user():
    # Ensure that the uploads folder for this user exists
    uf = os.path.join(app.config['upload_folder'], session["user"]["email"])
    Path(uf).mkdir(parents=True, exist_ok=True)
    return uf


def index_page():
    return app.send_static_file("default.html")


@auth_check
def home():
    return ok_json("Welcome HOME!")


@auth_check(roles=["ACA", "SUP", "DEA"])
def get_active_users():
    try:
        users = []
        for k in list(app.active_users.keys()):
            v = app.active_users.get(k)
            # Older than 30 minutes are inactive
            sec_since_last_access = (DT.now() - v).total_seconds()
            if sec_since_last_access < 1800:
                users.append("{0}. | Last access {1:.2f} min ago".format(k, sec_since_last_access/60))
            else:
                app.active_users.pop(k, None)
        
        return ok_json(users)
    except Exception as ex:
        msg = "Failed to get active users."
        logging.exception(msg)
        return error_json(msg)


def update_active_users():
    if "user" in session:
        app.active_users[current_user_name_login()] = DT.now()


def logout(send_response=True):
    app.active_users.pop(current_user_name_login(), None)
    session.pop('user', None)
    if send_response:
        return ok_json("Logged out.")


def get_my_doc_types_menus():
    my_role = current_role()
    dtq = DocAction.select(DocType).join(DocType)
    dtq = dtq.where(DocAction.user_role.in_(["ANY", my_role])).distinct()
    dt = {}
    for obj in dtq:
        if obj.group not in dt:
            dt[obj.group] = {"label": obj.group, "items": []}
        
        # Route's link pattern must match the one in VueJS router config
        mi = {"label": obj.name, 
                "href": "#/doc_find/{0}/{1}".format(obj.group, obj.name),
                "roles": "*"}
        dt[obj.group]["items"].append(mi)
    
    return dt.values()



def make_nav(role):
    try:
        # TODO: Cache the navs to avoid recomputing
        links, menus = [], []
        with open(os.path.join(app.root_path, "nav.json"), "r") as nd:
            nav = json.load(nd)
            for l in nav.pop("links"):
                r = l.pop("roles")
                if "*" in r or role in r:
                    links.append(l)
            
            for m in nav.pop("menus"):
                mi = []
                for i in m["items"]:
                    r = i.pop("roles")
                    if "*" in r or role in r:
                        mi.append(i)
                if mi:
                    m["items"] = mi
                    menus.append(m)

        # m2 = get_my_doc_types_menus()
        # menus.extend(m2)
        return {"menus": menus, "links": links}

    except Exception as ex:
        logging.exception("Error occurred when loading nav data.")


def extract_result_set(cursor):
    ncols = len(cursor.description)
    colnames = [cursor.description[i][0] for i in range(ncols)]
    results = []

    for row in cursor.fetchall():
        res = {}
        for i in range(ncols):
            res[colnames[i]] = row[i]
        results.append(res)
    
    return results
