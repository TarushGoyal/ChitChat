# main.py

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .models import *

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    dms = [i.id2 for i in DM.query.filter(DM.id1==1).all()]
    servers = [i.name for i in Server.query.join(ServerUser).filter(ServerUser.user_id == current_user.id).all()]
    #[i.server_id for i in ServerUser.query.filter(ServerUser.user_id==current_user.id).all()]
    return render_template('profile.html', name=current_user.name, dms=dms, servers=servers)

@main.route('/users')
@login_required
def users():
	data = [i.id for i in User.query.all()]
	return {
		"data" : data
	}
