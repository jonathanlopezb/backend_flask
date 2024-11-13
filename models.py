from flask_login import UserMixin
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from utils import *
from config import *
from datetime import datetime


bcrypt = Bcrypt(app)

# Modelos de la base de datos

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(100), unique=True, nullable=False)
    numero_identificacion = db.Column(db.String(20), unique=True, nullable=False)
    contraseña = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(20), nullable=False)
    

    def verificar_contraseña(self, contraseña):
        return check_password_hash(self.contraseña, contraseña)

class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    numero_identificacion = db.Column(db.String(20), unique=True, nullable=False)
    telefono = db.Column(db.String(15))
    email = db.Column(db.String(100))
    direccion = db.Column(db.String(150))
    cobrador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)

    cobrador = db.relationship("Usuario", backref="clientes_asignados", foreign_keys=[cobrador_id])
    prestamos = db.relationship('Prestamo', backref='cliente', lazy=True)


class Prestamo(db.Model):
    __tablename__ = 'prestamos'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    cobrador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    monto_prestado = db.Column(db.Float, nullable=False)
    numero_cuota = db.Column(db.Integer, nullable=False)
    cuotas_saldadas = db.Column(db.Integer, default=0)
    valor_cuota = db.Column(db.Float, nullable=False)
    saldo_pendiente = db.Column(db.Float, nullable=False)
    total_deuda = db.Column(db.Float, nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_termino = db.Column(db.Date, nullable=False)
    fecha_saldado = db.Column(db.DateTime, nullable=True)
    estado = db.Column(db.String(10), default="activo")

    cliente = db.relationship('Cliente', backref='prestamos')
    cobrador = db.relationship('Usuario', backref='prestamos')


# Crear las tablas en la base de datos
with app.app_context():
    db.create_all()