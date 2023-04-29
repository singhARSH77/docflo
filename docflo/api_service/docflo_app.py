"""Main entry script for the flask web application.

__author__ = "Balwinder Sodhi"
__copyright__ = "Copyright 2022"
__license__ = "MIT"
__version__ = "0.1"
__status__ = "Development"
"""
import getpass
import argparse
import json
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
from flask import Flask
from bg_tasks import *

# Configure the logging first
rfh_info = RotatingFileHandler("server_docflo.log", maxBytes=2000000, backupCount=10)
rfh_info.setLevel(logging.INFO)
rfh_error = RotatingFileHandler("server_docflo_error.log", maxBytes=1000000, backupCount=10)
rfh_error.setLevel(logging.WARNING)
logging.basicConfig(level=logging.DEBUG, handlers=[rfh_info, rfh_error],
                    format='%(asctime)s %(levelname)s:: %(message)s',
                    datefmt='%d-%m-%Y@%I:%M:%S %p')

import common as C
import views_all as V

TS_FORMAT = "%Y%m%d_%H%M%S"

def _setup_routes():
    # The root path simply returns the index.html
    V.vbp.add_url_rule('/', view_func=V.index_page, methods=['GET'])
    V.vbp.add_url_rule('/oauth/<token>', view_func=V.oauth_verify, methods=['GET'])
    V.vbp.add_url_rule('/logout', view_func=V.logout, methods=['GET', 'POST'])
    V.vbp.add_url_rule('/user/<int:user_id>', view_func=V.view_user, methods=['GET'])
    V.vbp.add_url_rule('/user_save', view_func=V.save_user, methods=['POST'])
    V.vbp.add_url_rule('/user_find', view_func=V.find_user, methods=['POST'])
    V.vbp.add_url_rule('/current_user', view_func=V.current_user, methods=['GET'])
    V.vbp.add_url_rule('/get_static_data', view_func=V.get_static_data, methods=['GET'])
    V.vbp.add_url_rule('/get_file/<string:file_name>', view_func=V.get_file, methods=['GET'])
    V.vbp.add_url_rule('/to_user/<int:myid>', view_func=V.to_user, methods=['GET'])
    V.vbp.add_url_rule('/user_lookup/<string:qry>', view_func=V.lookup_user, methods=['GET'])
    
    V.vbp.add_url_rule('/list_form_actions', view_func=V.all_form_actions, methods=['GET'])
    V.vbp.add_url_rule('/fa_save', view_func=V.save_form_action, methods=['POST'])
    V.vbp.add_url_rule('/fa_delete/<int:fa_id>', view_func=V.delete_form_action, methods=['GET'])
    V.vbp.add_url_rule('/my_form_actions/<int:doc_type>/<string:status>', view_func=V.get_form_actions, methods=['GET'])

    V.vbp.add_url_rule('/all_doc_types/<int:flatten>', view_func=V.get_all_doc_types, methods=['GET'])
    V.vbp.add_url_rule('/doc_type/<int:my_id>', view_func=V.get_doc_type, methods=['GET'])
    V.vbp.add_url_rule('/doc_type_search', view_func=V.find_doc_type, methods=['POST'])
    V.vbp.add_url_rule('/doc_type_save', view_func=V.save_doc_type, methods=['POST'])
    V.vbp.add_url_rule('/dtf_save', view_func=V.save_doc_field, methods=['POST'])
    V.vbp.add_url_rule('/dtf_delete/<int:my_id>', view_func=V.delete_doc_field, methods=['GET'])
    V.vbp.add_url_rule('/dtf_get/<int:my_id>', view_func=V.get_doc_type_fields, methods=['GET'])
    V.vbp.add_url_rule('/dtff_get/<int:my_id>', 
        view_func=V.get_finder_fields_for_doc, methods=['GET'])

    V.vbp.add_url_rule('/doc_item_save', view_func=V.save_doc_item, methods=['POST'])
    V.vbp.add_url_rule('/doc_item_get/<int:my_id>', view_func=V.get_doc_item, methods=['GET'])
    V.vbp.add_url_rule('/doc_item_search', view_func=V.find_doc_items, methods=['POST'])

def create_app(cfg_file_path, is_testing=False):
    myapp = Flask(__name__, static_folder="./app", static_url_path="/docflo/")
    myapp.secret_key = C.random_str(size=30)
    myapp.json_encoder = C.JSONEncoderWithDate
    myapp.active_users = {}

    with open(cfg_file_path, "r") as cfg_file:
        cfg = json.load(cfg_file)
        if not cfg["email"]["password"]:
            cfg["email"]["password"] = getpass.getpass("SMTP password:")
        if not cfg["db_args"]["password"]:
            cfg["db_args"]["password"] = getpass.getpass("DB password:")
        myapp.config.update(cfg)

    myapp.context_processor(C.inject_user)
    myapp.before_request(C.db_connect)
    myapp.after_request(C.db_close)
    myapp.before_request(V.update_active_users)

    # Add custom filters
    myapp.add_template_filter(C.jinja2_filter_datefmt, "datefmt")

    logger = logging.getLogger('peewee')
    if "peewee_debug" in myapp.config and myapp.config["peewee_debug"]:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Initialize uploads folder
    print("\n!!!!! Current working directory: {}\n".format(os.getcwd()))
    uploads = myapp.config['upload_folder']
    udp = Path(uploads)
    udp.mkdir(parents=True, exist_ok=True)
    myapp.config['upload_folder'] = udp.absolute()

    # Register views
    _setup_routes()
    
    # Register the blueprint for the application
    myapp.register_blueprint(V.vbp, url_prefix='/docflo')

    C.emailer.configure(myapp.config["email"])
    
    # Start the scheduler
    if not is_testing:
        bgt = BgTasks(myapp.config)
        # Run every day
        # bgt.add_job(V.schedule_alerts,
        #     {"id": "SendUserAlerts",
        #     "trigger": "interval", "days": 1
        #     })
        
        # bgt.start()
    
    return myapp


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", type=bool, nargs='?',
                        const=True, default=False,
                        dest="debug", help="Run the server in debug mode.")
    parser.add_argument("cfg_file_path", type=str,
                        help="Configuration file path.")
    args = parser.parse_args()
    app = create_app(args.cfg_file_path)
    app.run(host=app.config["host"], port=app.config["port"],
            threaded=True, debug=args.debug)
