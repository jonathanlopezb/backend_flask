from flask_login import UserMixin
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt

import datetime
from utils import *
from config import *

bcrypt = Bcrypt(app)

# Modelo Usuario
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(50), nullable=False, unique=True)
    numero_identificacion = db.Column(db.String(20), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    rol = db.Column(db.String(20), nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


# Modelo Cliente
class Cliente(db.Model):
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    numero_identificacion = db.Column(db.String(20), nullable=False, unique=True)
    celular = db.Column(db.String(20), nullable=False, unique=True)


    prestamos = db.relationship('Prestamo', back_populates="cliente")


# Modelo Prestamo
class Prestamo(db.Model):
    __tablename__ = 'prestamos'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    cobrador_id = db.Column(db.Integer, nullable=False)
    monto_prestado = db.Column(db.Float, nullable=False)
    numero_cuota = db.Column(db.Integer, nullable=False)
    valor_cuota = db.Column(db.Float, nullable=False)
    valor_saldado = db.Column(db.Float, nullable=False, default=0.0)
    saldo_pendiente = db.Column(db.Float, nullable=False)
    total_deuda = db.Column(db.Float, nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_termino = db.Column(db.Date, nullable=False)

    cliente = db.relationship('Cliente', back_populates="prestamos")


# Crear las tablas en la base de datos
with app.app_context():
    db.create_all()