from functools import wraps
from flask import g, request, redirect, url_for, render_template
from .models import *
from . import db
import inspect
from flask_login import login_required, current_user

def server_member(f):
    @wraps(f)
    def decorated_function(id, *args):
        print(inspect.getargspec(f))
        user = current_user
        print(id, user.id)
        if ServerUser.query.get((id,user.id)):
            return f(id)
        else:
            return render_template("error.html", error = "You are not a member of this server or have been kicked out")
    return decorated_function

def server_admin(f):
    @wraps(f)
    def decorated_function(server_id, *args, **kwargs):
        user = current_user
        su = ServerUser.query.get((server_id,user.id))
        if su and (su.role == 'Creator' or su.role == 'Admin'):
            return f(server_id, *args, **kwargs)
        else:
            return render_template("error.html", error = "You are not an admin of this server or have been demoted")
    return decorated_function
