"""Defines all the models used in this application.

__author__ = "Balwinder Sodhi"
__copyright__ = "Copyright 2022"
__license__ = "MIT"
__version__ = "0.1"
__status__ = "Development"
"""

import logging

from peewee import *
from playhouse.mysql_ext import JSONField

# Deferred initialization
db = MySQLDatabase(None)
    
class MediumTextField(TextField):
    field_type = "MEDIUMTEXT"


class MediumBlobField(BlobField):
    field_type = "MEDIUMBLOB"


def create_schema():
    logging.info("Creating DB tables")
    with db:
        db.create_tables(
            [SystemSetting, User, DocAction, AuditLog,
            DocItem, DocField, DocFieldValue, DocType,
            DocItemFile, DocItemNote]
        )
        logging.info("DB tables created.")


class AuditLog(Model):
    id = AutoField()
    entity_id = BigIntegerField()
    entity_name = CharField(max_length=255)
    old_row_data = JSONField()
    dml_type = CharField(max_length=20)
    dml_timestamp = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    dml_created_by = CharField(max_length=100, null=True)

    class Meta:
        database = db
        only_save_dirty = True
        indexes = (
            # Unique index
            (("entity_id", "entity_name", "dml_type"), True),
        )


class BaseModel(Model):
    id = AutoField()
    is_deleted = BooleanField(constraints=[SQL('DEFAULT FALSE')])
    txn_no = IntegerField(constraints=[SQL('DEFAULT 1')], index=True)
    ins_ts = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    ins_by = CharField(max_length=60, null=True)
    upd_ts = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    upd_by = CharField(max_length=60, null=True)

    class Meta:
        database = db
        only_save_dirty = True


class SystemSetting(BaseModel):
    group = CharField(max_length=60, index=True)
    name = CharField(max_length=200, index=True)
    is_json = BooleanField(index=True)
    value_text = TextField(null=True)
    value_json = JSONField(default={}, null=True)

    class Meta:
        indexes = (
            # Unique index
            (("group", "name", "is_json"), True),
        )


class User(BaseModel):
    email = CharField(max_length=100, unique=True)
    role = CharField(max_length=10)
    org_unit = CharField(max_length=60)
    first_name = CharField(max_length=200, null=True)
    last_name = CharField(max_length=200, null=True)
    is_locked = BooleanField(constraints=[SQL('DEFAULT FALSE')])

    def to_string(self):
        return "{0} {1} ({2})".format(self.first_name, 
            self.last_name, self.email)


class DocType(BaseModel):
    name = CharField(max_length=60, index=True)
    group = CharField(max_length=60, index=True)
    description = TextField(null=True)

    class Meta:
        indexes = (
            (("name", "group"), True),
        )


class DocField(BaseModel):
    doc_type = ForeignKeyField(DocType, backref="doc_fields")
    name = CharField(max_length=60, index=True)
    # float, integer, string, date, boolean
    field_type = CharField(max_length=60)
    optional = BooleanField(constraints=[SQL('DEFAULT FALSE')])
    finder = BooleanField(constraints=[SQL('DEFAULT FALSE')])
    display_seq = SmallIntegerField(default=0)
    label = CharField(max_length=100)

    class Meta:
        indexes = ()


class DocItem(BaseModel):
    doc_type = ForeignKeyField(DocType, backref="doc_items")
    status = CharField(max_length=40)


class DocItemFile(BaseModel):
    doc_item = ForeignKeyField(DocItem, backref="doc_files")
    # UUID value
    doc_file = TextField()


class DocItemNote(BaseModel):
    doc_item = ForeignKeyField(DocItem, backref="doc_notes")
    author = ForeignKeyField(User, backref="user_notes")
    note = TextField()


class DocFieldValue(BaseModel):
    doc_field = ForeignKeyField(DocField, backref="field_values")
    doc_item = ForeignKeyField(DocItem, backref="field_values")
    field_val = CharField(max_length=150, null=True)


class DocAction(BaseModel):
    doc_type = ForeignKeyField(DocType, backref="doc_actions")
    user_role = CharField(max_length=10)
    status_now = CharField(max_length=40)
    action = CharField(max_length=60)
    status_after = CharField(max_length=40, null=True)
    allowed_ou = CharField(max_length=60)

    class Meta:
        indexes = (
            # Unique index
            (("doc_type", "user_role", "status_now", "action"), True),
        )
