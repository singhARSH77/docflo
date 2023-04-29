"""View functions for managing the API.

__author__ = "Balwinder Sodhi"
__copyright__ = "Copyright 2022"
__license__ = "MIT"
__version__ = "0.1"
__status__ = "Development"
"""

from functools import reduce
import operator
import uuid
from flask import request
from werkzeug.utils import secure_filename
from views_common import *


def _get_my_doc_item_ids():
    cu = session_user()
    my_role, my_ou = cu["role"], cu["org_unit"]

    daq = DocItem.select().join(DocType).join(DocAction)
    daq = daq.where(DocAction.user_role.in_(["ANY", my_role]))
    # daq = daq.where((DocAction.status_now == "ANY") |
    #             (DocAction.status_now == DocItem.status))
    daq = daq.where(
        (DocAction.allowed_ou.in_(["*", my_ou])) |
        ((DocAction.allowed_ou == ".") &
         (my_ou == (User.select(User.org_unit).where(User.email == DocItem.ins_by)))
        )
        )
    
    return [x.id for x in daq]


def _check_doc_action(doc_type_id, ins_by, status=None):
    if is_user_in_role("SUP"):
        return # Superuser is allowed all actions
    
    cu = session_user()
    my_role, my_ou = cu["role"], cu["org_unit"]
    uq=User.select().where(User.email == ins_by)
    item_ou = None
    if uq.exists():
        item_ou = uq[0].org_unit
    daq = DocAction.select().where(DocAction.doc_type == doc_type_id)
    if status:
        daq = daq.where(DocAction.status_now.in_([status, "ANY"]))
    daq = daq.where(DocAction.user_role.in_(["ANY", my_role]))
    daq = daq.where(
        (DocAction.allowed_ou.in_(["*", my_ou])) |
        ((DocAction.allowed_ou == ".") & (item_ou == my_ou))
        )
    
    if not daq.exists():
        raise AppException("Change not allowed.")


def _save_uploaded_file(dataFile, dataType):
    if dataFile.filename == '':
        raise AppException("Please select the data file. No file supplied!")
    orig_fn = secure_filename(dataFile.filename)
    filename = "DAT_{0}_{1}_._{2}".format(dataType, uuid.uuid4(), orig_fn)
    file_path = os.path.join(get_upload_folder(), filename)
    dataFile.save(file_path)
    return file_path, filename


@auth_check(roles=["SUP"])
def data_import():
    try:
        dataType = request.form.get('dataType')
        dataFile = request.files['dataFile']
        file_path, fn = _save_uploaded_file(dataFile, dataType)
        rows = 0
        # if dataType == "TAX":
        #     rows = taxonomy_import(file_path)
        # elif dataType == "OBK":
        #     rows = books_import(file_path, False)
        # else:
        #     return error_json("Invalid data type {}".format(dataType))
        
        return ok_json("Imported {0} data records.".format(rows))

    except Exception as ex:
        msg = "Error when importing data. Cause: {}".format(ex)
        if isinstance(ex, KeyError):
            msg = "Incorrect header field(s) in CSV file: {}".format(ex)
        logging.exception(msg)
        return error_json(msg)


def _get_audit(ent_id, ent_name):
    las = AuditLog.select(AuditLog.old_row_data, AuditLog.dml_type)
    las = las.where(AuditLog.entity_id==ent_id)
    las = las.where(AuditLog.entity_name==ent_name)
    las = las.where(AuditLog.dml_type=="UPDATE")
    lst = [model_to_dict(x) for x in las]
    return lst


@auth_check
def get_form_actions(doc_type, status):
    try:
        qry = DocAction.select()
        qry = qry.where(DocAction.doc_type == doc_type)
        qry = qry.where(DocAction.status_now.in_([status, "ANY"]))
        if not is_user_in_role("SUP"):
            qry = qry.where(DocAction.user_role.in_([current_role(), "ANY"]))
        ser = [{"arg": x.status_after, "label": x.action} 
                for x in qry.distinct()]
        return ok_json(ser)
    except Exception as ex:
        msg = log_error(ex, "Error when loading form actions for this user.")
        return error_json(msg)


@auth_check(roles=["SUP"])
def all_form_actions():
    try:
        qry = DocAction.select()
        ser = [model_to_dict(x, recurse=False) for x in qry]
        return ok_json(ser)
    except Exception as ex:
        msg = log_error(ex, "Error when loading form actions.")
        return error_json(msg)


@auth_check(roles=["SUP"])
def save_form_action():
    try:
        fd = request.get_json(force=True)
        fa_id = fd.get("id", 0)
        ra = DocAction.get_by_id(fa_id) if fa_id else DocAction()
        merge_json_to_model(ra, fd)
        if fa_id:
            rc = update_entity(DocAction, ra)
        else:
            ra.user = logged_in_user().id
            rc = save_entity(ra)
        if rc != 1:
            return error_json("Could not save the form action.")
        
        ra = DocAction.get_by_id(ra.id)
        res = model_to_dict(ra)
        return ok_json(res)
    except Exception as ex:
        msg = log_error(ex, "Error when saving form action.")
        return error_json(msg)


@auth_check(roles=["SUP"])
def delete_form_action(fa_id):
    try:
        act = DocAction.get_by_id(fa_id)
        rc = act.delete_instance()
        if rc == 1:
            return ok_json("Deleted the form action.")
        else:
            return error_json("Failed to delete the form action.")
    except Exception as ex:
        msg = log_error(ex, "Error when deleting form action.")
        return error_json(msg)


@auth_check(roles=["SUP"])
def delete_doc_field(my_id):
    try:
        act = DocField.get_by_id(my_id)
        rc = act.delete_instance()
        if rc == 1:
            return ok_json("Deleted the doc field.")
        else:
            return error_json("Failed to delete the doc field.")
    except Exception as ex:
        msg = log_error(ex, "Error when deleting doc field.")
        return error_json(msg)

@auth_check
def get_doc_type_fields(my_id):
    try:
        dtq = DocType.get_by_id(my_id)
        dfq = dtq.doc_fields
        dfq = dfq.order_by(DocField.display_seq)
        df = [model_to_dict(x, recurse=False) for x in dfq]
        return ok_json(df)
    except Exception as ex:
        msg = log_error(ex, "Error loading doc fields.")
        return error_json(msg)


@auth_check
def get_finder_fields_for_doc(my_id):
    try:
        doct = DocType.get_by_id(my_id)
        dfq = doct.doc_fields.where(DocField.finder == True)
        dfq = dfq.order_by(DocField.display_seq)
        df = [model_to_dict(x, recurse=False) for x in dfq]
        return ok_json(df)
    except Exception as ex:
        msg = log_error(ex, "Error loading finder fields.")
        return error_json(msg)


@auth_check(roles=["SUP"])
def save_doc_field():
    try:
        fd = request.get_json(force=True)
        fa_id = fd.get("id", 0)
        ra = DocField.get_by_id(fa_id) if fa_id else DocField()
        merge_json_to_model(ra, fd)
        if fa_id:
            rc = update_entity(DocField, ra)
        else:
            rc = save_entity(ra)
        if rc != 1:
            return error_json("Could not save the doc field.")
        
        ra = DocField.get_by_id(ra.id)
        res = model_to_dict(ra, recurse=False)
        return ok_json(res)
    except Exception as ex:
        msg = log_error(ex, "Error when saving doc field.")
        return error_json(msg)


@auth_check(roles=["SUP"])
def save_doc_type():
    try:
        fd = request.get_json(force=True)
        fa_id = fd.get("id", 0)
        ra = DocType.get_by_id(fa_id) if fa_id else DocType()
        merge_json_to_model(ra, fd)
        if fa_id:
            rc = update_entity(DocType, ra)
        else:
            rc = save_entity(ra)
        if rc != 1:
            return error_json("Could not save the doc type.")
        else:
            res = model_to_dict(ra)
            return ok_json(res)
    except Exception as ex:
        msg = log_error(ex, "Error when saving doc type.")
        return error_json(msg)


@auth_check(roles=["SUP"])
def find_doc_type():
    try:
        fd = request.get_json(force=True)
        name = fd.get("name")
        pg_no = int(fd.get('pg_no', 1))
        dtq = DocType.select()
        dtq = dtq.where(DocType.is_deleted != True)
        if name:
            dtq = dtq.where(DocType.name.contains(name))
        data = dtq.order_by(-DocType.id).paginate(pg_no, PAGE_SIZE)
        serialized = [model_to_dict(r) for r in data]
        has_next = len(data) >= PAGE_SIZE
        res = {"items": serialized, "pg_no": pg_no, "pg_size": PAGE_SIZE,
               "has_next": has_next}
        return ok_json(res)
    except Exception as ex:
        msg = log_error(ex, "Error when searching doc type.")
        return error_json(msg)


@auth_check(roles=["SUP"])
def get_doc_type(my_id):
    try:
        dt = DocType.get_by_id(my_id)
        df = [model_to_dict(x, recurse=False) for x in dt.doc_fields]
        res = model_to_dict(dt, recurse=False)
        res["doc_fields"] = df
        return ok_json(res)
    except Exception as ex:
        msg = log_error(ex, "Error when fetching doc type.")
        return error_json(msg)


@auth_check
def get_all_doc_types(flatten=0):
    try:
        dt = DocType.select()
        data = [] if flatten else {}
        for x in dt:
            if flatten:
                val = "{0} / {1}".format(x.group, x.name)
                data.append({"id": x.id, "value": val})
            else:
                if x.group not in data:
                    data[x.group] = []
                grp_items = data.get(x.group)
                grp_items.append({"id": x.id, "value": x.name})
        
        return ok_json(data)
    except Exception as ex:
        msg = log_error(ex, "Error when fetching doc types.")
        return error_json(msg)


def _fetch_doc_item(item):
    di = DocItem.get_by_id(item) if isinstance(item, int) else item
    df = [f.doc_file for f in di.doc_files]
    dn = []
    for n in di.doc_notes:
        obj = model_to_dict(n, recurse=False)
        obj["author"] = model_to_dict(n.author, recurse=False)
        dn.append(obj)
    
    data = model_to_dict(di, recurse=False)
    data["doc_files"] = df
    data["doc_notes"] = dn
    for fv in di.field_values:
        data["__DF{0}".format(fv.doc_field.id)] = fv.field_val
    return data


@auth_check
def get_doc_item(my_id):
    try:
        di = DocItem.get_by_id(my_id)
        _check_doc_action(di.doc_type.id, di.ins_by)
        data = _fetch_doc_item(my_id)
        return ok_json(data)
    except Exception as ex:
        msg = log_error(ex, "Error when fetching doc item.")
        return error_json(msg)


@auth_check
def save_doc_item():
    try:
        fd = {}
        for (k, v) in request.form.items():
            if v not in ["null", "undefined", ""]:
                if v == "true":
                    fd[k] = True
                elif v == "false":
                    fd[k] = False
                else:
                    fd[k] = v
        
        editing = "id" in fd
        dfl = request.files.getlist("dataFiles")
        files_info = []
        for file in dfl:
            file_path, fname = _save_uploaded_file(file, "DOCITEM")
            files_info.append((file_path, fname))
        cu = session_user()
        di = DocItem.get_by_id(int(fd["id"])) if editing else DocItem()
        status_now = di.status
        merge_json_to_model(di, fd)
        dtid = fd["doc_type"]
        _check_doc_action(dtid, di.ins_by if editing else cu["email"], status_now)

        with db.transaction() as txn:
            rc = 0
            if editing:
                rc = update_entity(DocItem, di)
            else:
                rc = save_entity(di)
            if rc != 1:
                raise AppException("Failed to save doc item. Please retry later.")

            din = DocItemNote(doc_item=di.id, note=fd["action_note"])
            din.author = cu["id"]
            rc += save_entity(din)

            for fin in files_info:
                dif = DocItemFile(doc_item=di.id, doc_file=fin[1])
                rc += save_entity(dif)
            
            if rc != len(files_info) + 2:
                raise AppException("Failed to save some items. Please retry later.")

            DFV = DocFieldValue
            dfvq = DFV.select(DFV.doc_field).where(DFV.doc_item == di.id)
            df_ids = [x.doc_field.id for x in dfvq]

            # Now add the new values
            for (k, v) in fd.items():
                if k.startswith("__DF"):
                    if int(k[4:]) in df_ids:
                        q1 = DFV.select().where(DFV.doc_item == di.id)
                        q1 = q1.where(DFV.doc_field == int(k[4:]))
                        dfv = q1[0]
                        dfv.field_val = v
                        rc = update_entity(DocFieldValue, dfv)
                    else:
                        dfv = DocFieldValue(doc_item=di.id)
                        dfv.doc_field=int(k[4:])
                        dfv.field_val = v
                        rc = save_entity(dfv)
                    
                    if rc == 0:
                        raise AppException("Failed to save field value!")

        res = _fetch_doc_item(int(di.id))
        return ok_json(res)
    except Exception as ex:
        msg = log_error(ex, "Error when saving doc item.")
        return error_json(msg)


def find_doc_items():
    try:
        fd = request.get_json(force=True)
        dt_id, status = fd.get("doc_type"), fd.get("status")
        fc_min, fc_max = fd.get("min_files"), fd.get("max_files")
        note = fd.get("note")
        crtr, updt = int(fd.get("creator", 0)), int(fd.get("updater", 0))
        pg_no = int(fd.get('pg_no', 1))
        
        dtq = DocItem.select(DocItem, User) \
            .join(User, on=(User.email == DocItem.ins_by), attr='INSBY') \
            .switch(DocItem).join(DocType)
        dtq = dtq.where(DocType.id == dt_id)
        if status:
            dtq = dtq.where(DocItem.status == status)
        if crtr:
            ins_by = User.get_by_id(crtr).email
            dtq = dtq.where(DocItem.ins_by == ins_by)
        if updt:
            upd_by = User.get_by_id(updt).email
            dtq = dtq.where(DocItem.upd_by == upd_by)

        filtered_ids = set()
        if note:
            dnq = DocItemNote.select(DocItemNote.doc_item)
            dnq = dnq.where(DocItemNote.note.contains(note))
            dnq = dnq.group_by(DocItemNote.doc_item)
            dnq = dnq.having(fn.Count(DocItemNote.id) > 0)
            filtered_ids.update([x.doc_item.id for x in dnq] or [-1])
        
        dfq = DocItemFile.select(DocItemFile.doc_item)
        dfq = dfq.group_by(DocItemFile.doc_item)
        if fc_min != None:
            dfq = dfq.having(fn.Count(DocItemFile.id) >= fc_min)
        if fc_max != None:
            dfq = dfq.having(fn.Count(DocItemFile.id) <= fc_max)
        if fc_max != None or fc_min != None:
            filtered_ids.update([x.doc_item.id for x in dfq] or [-1])

        # Add filters for remaining criteria
        dfvq = DocFieldValue.select(DocFieldValue.doc_item)
        has_fv_crit = []
        for (k, v) in fd.items():
            if k.startswith("__DF"):
                has_fv_crit.append(
                    ((DocFieldValue.doc_field == int(k[4:])) &
                    (DocFieldValue.field_val == v)))
        if has_fv_crit:
            dfvq = dfvq.where(reduce(operator.or_, has_fv_crit)).distinct()
            filtered_ids.update([x.doc_item.id for x in dfvq] or [-1])
        
        if not is_user_in_role("SUP"):
            # Include only those items that are allowed for this user
            my_items = set(_get_my_doc_item_ids())
            if filtered_ids:
                filtered_ids.intersection_update(my_items)
            else:
                filtered_ids = my_items
            dtq = dtq.where(DocItem.id.in_(filtered_ids))
        elif filtered_ids:
            dtq = dtq.where(DocItem.id.in_(filtered_ids))
        
        data = dtq.order_by(-DocItem.id).paginate(pg_no, PAGE_SIZE)
        serialized = [model_to_dict(r) for r in data]
        has_next = len(data) >= PAGE_SIZE
        res = {"items": serialized, "pg_no": pg_no, "pg_size": PAGE_SIZE,
               "has_next": has_next}
        return ok_json(res)
    except Exception as ex:
        msg = log_error(ex, "Error when searching doc items.")
        return error_json(msg)
