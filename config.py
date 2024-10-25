from flask import Flask, request, jsonify
from flask_login import LoginManager, login_user, UserMixin, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_mail import Mail, Message
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import create_engine


app = Flask(__name__)
app.secret_key = 'eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJleHAiOjE3MzI0MjExNDIsImlhdCI6MTcyOTgyOTE0MiwiaWQiOiI5OWU4MzcwYS0yMmY1LTRmMDMtYjNmZC01NWVlNTI5OWM2MjMifQ.2sBLQAQCB3KboIucG_r_iqJE2BhJhmxb4unnQveQe0C4gapN7uWkHM7_-7DlhMfCqnbi0gZ0lwsqvTY_aKdZDg'

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite+libsql://sisuma-jonatanlopezb.aws-us-east-1.turso.io/?authToken=eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3Mjk4MjY2ODUsImlkIjoiOTllODM3MGEtMjJmNS00ZjAzLWIzZmQtNTVlZTUyOTljNjIzIn0.VkcVTdSNOZoOgHcq-3XuHniYArgxPhrfKXEgia1h9g3PrHRZ9mbb-ycGcuwNYeY1vSxO6Bb4v08dmwSHd3_8Dg&secure=true'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

print(app)

# Configuración del panel de administración
admin = Admin(app, name='Control Panel')

# Inicialización de Marshmallow
ma = Marshmallow(app)
db = SQLAlchemy(app)

# Configuración de login
login_manager = LoginManager()
login_manager.init_app(app)

# Configuración de correo
# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = 'correo'  # Cambia por tu correo
# app.config['MAIL_PASSWORD'] = 'contraseña del correo'  # Cambia por la contraseña de tu correo

mail = Mail(app)
