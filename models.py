import datetime
import random
import string

from peewee import *

db = SqliteDatabase('database.db')


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    user_id = IntegerField()
    login = TextField(default="Нет ника")
    username = TextField(default="")
    balance = IntegerField(default=0)
    role = IntegerField(default=1)


class Form(BaseModel):
    command = TextField()
    target = TextField()
    author = ForeignKeyField(User)
    status = IntegerField(default=0)
    created = DateTimeField(default=datetime.datetime.now)


class Issue(BaseModel):
    link = TextField()
    title = TextField(default="")
    last_interaction = ForeignKeyField(User, default=None, null=True)
    last_date = DateTimeField(default=datetime.datetime.now)
    created = DateTimeField(default=datetime.datetime.now)
    closed = BooleanField(default=False)


class Action(BaseModel):
    type = TextField()
    link = TextField()
    user = ForeignKeyField(User, default=None, null=True)
    message = TextField(default="")
    created = DateTimeField(default=datetime.datetime.now)
