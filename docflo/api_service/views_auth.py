"""View functions for managing the users and authentication tasks.

__author__ = "Balwinder Sodhi"
__copyright__ = "Copyright 2022"
__license__ = "MIT"
__version__ = "0.1"
__status__ = "Development"
"""

from flask import request
from flask.helpers import send_file
from google.auth.transport import requests
from google.oauth2 import id_token
from werkzeug.utils import secure_filename

from views_common import *


def _item_label(item_code, items_map):
    long_label = item_code
    for y in items_map:
        ct = item_code
        if ct == y["id"]:
            long_label = y["value"]
            break

    return long_label


@auth_check
def get_static_data():
    try:
        sd = static_data_dict()
        qry = User.select().where(User.is_deleted==False)
        sd["UsersList"] = [{"id": u.id, \
                            "value": "{0} ({1})".format(u.to_string(), \
                            _item_label(u.role, sd["UserRoles"]))} \
                            for u in qry]
        return ok_json(sd)
    except Exception as ex:
        msg = log_error(ex, "Error when loading static data.")
        return error_json(msg)


@auth_check
def lookup_user(qry):
    try:
        query = User.select()
        query = query.where(User.is_deleted != True)
        query = query.where((User.first_name.contains(qry)) |
                            (User.last_name.contains(qry)))
        users = query.order_by(-User.id)
        res = [model_to_dict(r) for r in users]
        return ok_json(res)

    except Exception as ex:
        msg = log_error(ex, "Error when looking up users.")
        return error_json(msg)


@auth_check
def find_user():
    try:
        fd = request.get_json(force=True)
        name, role = fd.get("name"),fd.get("role")
        email, org_unit = fd.get("email"), fd.get("area")
        
        roles = []
        if role:
            roles.append(role)

        pg_no = int(fd.get('pg_no', 1))
        query = User.select()
        query = query.where(User.is_deleted != True)
        if roles:
            query = query.where(User.role.in_(roles))
        if email:
            query = query.where(User.email.contains(email))
        if name:
            query = query.where((User.first_name.contains(name)) |
                                (User.last_name.contains(name)))
        if org_unit:
            query = query.where(User.org_unit == org_unit)

        users = query.order_by(-User.id).paginate(pg_no, PAGE_SIZE)
        serialized = [model_to_dict(r) for r in users]
        has_next = len(users) >= PAGE_SIZE
        res = {"users": serialized, "pg_no": pg_no, "pg_size": PAGE_SIZE,
               "has_next": has_next}
        return ok_json(res)

    except Exception as ex:
        msg = log_error(ex, "Error when finding users.")
        return error_json(msg)


@auth_check
def view_user(user_id):
    try:
        cu = logged_in_user()
        res = User.select().where(User.id == user_id)
        if not res.exists():
            return error_json("Failed to locate the user!")        
        if not is_user_in_role("SUP") and cu.id != res[0].id:
            return error_json("Cannot access other's profile!")
        uobj = model_to_dict(res[0], recurse=False)
        return ok_json(uobj)

    except Exception as ex:
        msg = log_error(ex, "Error when fetching User details.")
        return error_json(msg)

    
@auth_check(roles=["SUP"])
def save_user():
    try:
        fd = request.get_json(force=True)
        logging.info("Saving user details: {}".format(fd))
        cid = int(fd.get("id") or 0)
        user_mod = User.get_by_id(cid) if cid else User()
        merge_json_to_model(user_mod, fd)
        with db.atomic() as txn:
            rc = 0
            if cid:        
                rc = update_entity(User, user_mod)
            else:
                rc = save_entity(user_mod)
             
            if rc != 1:
                return error_json("Could not save user details. Please try again.")
            logging.debug("Saved user details: {}".format(user_mod))
                        
            txn.commit()

            # Send email notification of new user creation
            if not cid:
                send_user_creation_email(fd.get("email"))
            
        return view_user(user_id=user_mod.id)

    except Exception as ex:
        msg = log_error(ex, "Error when saving User details.")
        return error_json(msg)


@auth_check
def get_file(file_name):
    try:
        fp = os.path.join(get_upload_folder(), secure_filename(file_name))
        return send_file(fp)
    except Exception as ex:
        msg = log_error(ex, "Error when loading image.")
        return error_json(msg)


def signin_user(my_id, isEmail=True):
    u = None
    if isEmail:
        u = User.get_or_none(User.email == my_id)
    else:
        u = User.get_or_none(User.id == my_id)
    
    if u:
        if u.is_locked:
            raise AppException("User is locked! Please contact admin.")
    else:
        raise AppException("The user with email {0} not found!".format(my_id))

    logging.info("Got user: {0} ({1})".format(u.first_name, u.email))        
    session['user'] = model_to_dict(u)
    return session['user']


def oauth_verify(token):
    """
    Validate the OAuth token with Google OAuth
    """
    try:
        # Specify the CLIENT_ID of the app that accesses the backend
        CLIENT_ID = "453234912886-rceu01gos16kfn79t0q5cfkqt1ppl6rr.apps.googleusercontent.com"
        idinfo = id_token.verify_oauth2_token(token,
                                              requests.Request(), CLIENT_ID)

        # If auth request is from a domain:
        # if idinfo['hd'] != "example.in":
        #     raise ValueError('Wrong hosted domain.')

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        email_id = idinfo['email']
        signin_user(email_id)
        return ok_json("OAuth Login successful.")

    except Exception as ve:
        # Invalid token
        msg = "Failed to complete authentication. "
        if isinstance(ve, OperationalError):
            msg += "Could not connect to DB."
        logging.exception(msg, ve)
        return error_json(msg)


@auth_check(roles=["SUP"])
def delete_user(my_id):
    rc = User.delete_by_id(my_id)
    if rc == 1:
        return ok_json("User deleted!")
    else:
        return error_json("Failed to delete user.")


@auth_check(roles=["SUP"])
def to_user(myid):
    try:
        signin_user(myid, isEmail=False)
        return ok_json("User changed!")
    except Exception as ex:
        msg = log_error(ex, "Failed to change to user.")
        return error_json(msg)
