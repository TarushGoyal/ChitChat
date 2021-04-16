# init.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy, event
from flask_login import LoginManager
from flask_restful import Api
from flask_socketio import SocketIO, emit

db = SQLAlchemy()
socketIO = SocketIO()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['UPLOAD_FOLDER'] = './static/files'

    db.init_app(app)
    with app.app_context():
        db.create_all()

    socketIO.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id)) # coz primary key

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .events import chat
    # @socketIO.on('send chat')
    # def chat(json, methods=['GET', 'POST']):
    #     print('received my event: ' + str(json))
    #     json['username'] = "Thinking..."
    #     socketIO.emit('add chat', json)

    return app
