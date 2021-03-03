# models.py

from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

class DM(db.Model):
    __tablename__ = "DM"
    id1 = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key=True)
    id2 = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key=True)

class Server(db.Model):
    __tablename__ = "Server"
    id = db.Column(db.Integer, primary_key=True)

class ServerUser(db.Model):
    __tablename__ = "ServerUser"
    server_id = db.Column(db.Integer, db.ForeignKey('Server.id'), primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key = True)
