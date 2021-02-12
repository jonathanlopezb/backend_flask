from flask_marshmallow import Marshmallow
import datetime
from utils import *
from config import *


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    identification = db.Column(db.String(100))
    address = db.Column(db.String(100))
    contact = db.Column(db.String(100))
    services = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    token_confirmations = db.Column(db.String(4))
    observation = db.relationship('Observation', backref='user')
    

    def __init__(self, email, password, name, confirmed, observation=None,
                 paid=False, is_admin=False, confirmed_on=None, token_confirmations=random_token()):
        self.email = email
        self.password = password
        self.name = name
        self.registered_on = datetime.datetime.now()
        self.is_admin = is_admin
        self.confirmed = confirmed
        self.confirmed_on = confirmed_on
        self.token_confirmations = token_confirmations


class UserSchema(ma.Schema):
    class Meta:
        fields = (  'id', 
                    'email', 
                    'name', 
                    'is_admin'
                    'identification',
                    'address',
                    'contact',
                    'services'
        )


user_schema = UserSchema()
users_schema = UserSchema(many=True)

class Observation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(70), unique=True)
    description = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    

    def __init__(self, title, description, user_id):
        self.title = title
        self.description = description
        self.user_id = user_id

db.create_all()

class ObservationSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'description', 'user_id', 'name')


observation_schema = ObservationSchema()
observations_schema = ObservationSchema(many=True)