from flask import Flask, request, jsonify
from flask_login import LoginManager, login_user, UserMixin, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_mail import Mail, Message
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import create_engine
from flask_cors import CORS


app = Flask(__name__)
app.secret_key = 'sisuma'

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite+libsql://sisuma-jonatanlopezb.turso.io/?authToken=eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3Mjk4MzI0NTMsImlkIjoiYjU5NjJmZDQtNDdkNi00ODZlLTlkZDQtNmRiZTliMGFjZTM5In0.0geswdgDlRWv5xmhEUiehPOmIntvt1XuqZ_bUwl1xg14cG92LQqMJAWANNke43el8_KtTFD1lU6qGmhJbkVbAA&secure=true'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
print(app)
CORS(app)

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
