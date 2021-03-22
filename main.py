# main.py

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from .models import *

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    servers = current_user.get_servers()
    return render_template('profile.html', name=current_user.name, servers=servers)

@main.route('/users')
def users():
	data = [i.id for i in User.get_all()]
	return {
		"data" : data
	}

@main.route('/server/<id>')
@login_required
def server(id):
	server = Server.query.get(id)
	return render_template('server.html',server = server,
                                         channels = server.get_channels(),
                                         members = server.get_users())

@main.route('/channel/<id>', methods = ['GET'])
@login_required
def channel(id):
    channel = Channel.query.get(id)
    return render_template('channel.html',channel = channel,
                                          members = channel.get_users())
