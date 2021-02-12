from flask import Flask, request, jsonify
from flask_login import login_manager, LoginManager, login_user, UserMixin, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

from flask_mail import Mail, Message


from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


from models import *



app = Flask(__name__)
app.secret_key = 'secreto'
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Lopez123*@localhost:5432/prueba'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



admin = Admin(app, name='Control Panel')

ma = Marshmallow(app)

login_manager = LoginManager()
login_manager.init_app(app)



app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'mnsneptuno@gmail.com'
app.config['MAIL_PASSWORD'] = '92021002749jona'

mail = Mail(app)