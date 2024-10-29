from flask import Flask, request, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash

from flask_mail import Mail, Message
from utils import random_token

from models import *
from config import *

from datetime import datetime

# from dotenv import load_dotenv
# from sqlalchemy import create_engine
# from sqlalchemy.orm import Session
# from sqlalchemy import select

# engine = create_engine(db, connect_args={'check_same_thread': False}, echo=True)

@app.errorhandler(404)
def not_found(error):
    return jsonify({'mensaje': 'Pagina no encontrada', 'error' : '404'})

@app.errorhandler(405)
def not_found(error):
    return jsonify({'mensaje': 'No encontramos tu requerimiento', 'error' : '405'})

@app.errorhandler(401)
def not_found(error):
    return jsonify({'mensaje': 'No encontramos tu requerimiento, Porfavor inicia sesion', 'error' : '401'})


@app.errorhandler(500)
def server_error(error):
    return jsonify({'mensaje': 'No encontramos tu requerimiento', 'error' : '500'})


@app.route('/', methods=['GET'])
def index():
    return jsonify({'message': 'Bienvenido a la prueba api-rest'})


# Rutas para Usuarios
@app.route('/registro', methods=['POST'])
def registrar_usuario():
    data = request.get_json()
    nombre_usuario = data.get('nombre_usuario')
    numero_identificacion = data.get('numero_identificacion')
    password = data.get('password')
    rol = data.get('rol')
    
    usuario = Usuario(
        nombre_usuario=nombre_usuario,
        numero_identificacion=numero_identificacion,
        rol=rol
    )
    usuario.set_password(password)
    db.session.add(usuario)
    db.session.commit()
    
    return jsonify({"message": f"Usuario '{nombre_usuario}' registrado con éxito", "id": usuario.id})


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    nombre_usuario = data.get('nombre_usuario')
    password = data.get('password')
    
    # Validar que ambos campos estén presentes
    if not nombre_usuario or not password:
        return jsonify({"error": "Nombre de usuario y contraseña son obligatorios"}), 400
    
    # Buscar el usuario en la base de datos
    usuario = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()
    
    # Validar existencia del usuario y coincidencia de contraseña
    if usuario and usuario.check_password(password):
        return jsonify({"status": "ok","message": "Inicio de sesión exitoso", "user_id": usuario.id, "rol": usuario.rol, 'user_name': usuario.nombre_usuario}), 200
    else:
        return jsonify({"error": "Nombre de usuario o contraseña incorrectos"}), 401
    

@app.route('/usuarios', methods=['GET'])
def obtener_usuarios():
    usuarios = Usuario.query.all()
    resultado = [
        {
            "id": usuario.id,
            "nombre_usuario": usuario.nombre_usuario,
            "numero_identificacion": usuario.numero_identificacion,
            "rol": usuario.rol
        } for usuario in usuarios
    ]
    return jsonify(resultado)

@app.route('/usuario/<int:id>', methods=['GET'])
def obtener_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    resultado = {
        "id": usuario.id,
        "nombre_usuario": usuario.nombre_usuario,
        "numero_identificacion": usuario.numero_identificacion,
        "rol": usuario.rol
    }
    return jsonify(resultado)

@app.route('/usuarios/cobradores', methods=['GET'])
def obtener_usuarios_cobradores():
    cobradores = Usuario.query.filter_by(rol="cobrador").all()
    resultado = [{"id": c.id, "nombre_usuario": c.nombre_usuario, "numero_identificacion": c.numero_identificacion, "rol": c.rol} for c in cobradores]
    return jsonify(resultado)

@app.route('/cobrador/<int:cobrador_id>/prestamos', methods=['GET'])
def obtener_cobrador_con_prestamos(cobrador_id):
    cobrador = Usuario.query.filter_by(id=cobrador_id, rol="cobrador").first()
    if not cobrador:
        return jsonify({"error": "Cobrador no encontrado o el usuario no es un cobrador"}), 404
    
    prestamos = Prestamo.query.filter_by(cobrador_id=cobrador_id).all()
    resultado = {
        "cobrador": {
            "id": cobrador.id,
            "nombre_usuario": cobrador.nombre_usuario,
            "numero_identificacion": cobrador.numero_identificacion,
            "rol": cobrador.rol
        },
        "prestamos": [
            {
                "id": prestamo.id,
                "cliente_id": prestamo.cliente_id,
                "nombre_cliente": prestamo.nombre,
                "monto_prestado": prestamo.monto_prestado,
                "numero_cuota": prestamo.numero_cuota,
                "valor_cuota": prestamo.valor_cuota,
                "valor_saldado": prestamo.valor_saldado,
                "saldo_pendiente": prestamo.saldo_pendiente,
                "total_deuda": prestamo.total_deuda
            } for prestamo in prestamos
        ]
    }
    return jsonify(resultado)

# Rutas para Clientes
@app.route('/cliente', methods=['POST'])
def crear_cliente():
    data = request.get_json()
    cliente = Cliente(
        nombre=data['nombre'],
        fecha_inicio=datetime.strptime(data['fecha_inicio'], '%Y-%m-%d'),
        fecha_termino=datetime.strptime(data['fecha_termino'], '%Y-%m-%d')
    )
    db.session.add(cliente)
    db.session.commit()
    return jsonify({"message": f"Cliente '{cliente.nombre}' creado con éxito", "id": cliente.id})

# Rutas para Préstamos
@app.route('/prestamo', methods=['POST'])
def registrar_prestamo():
    data = request.get_json()
    cliente_id = data.get('cliente_id')
    cobrador_id = data.get('cobrador_id')
    monto_prestado = data.get('monto_prestado')
    numero_cuota = data.get('numero_cuota')
    valor_cuota = data.get('valor_cuota')
    
    if not all([cliente_id, cobrador_id, monto_prestado, numero_cuota, valor_cuota]):
        return jsonify({"error": "Todos los campos son obligatorios"}), 400

    cliente = Cliente.query.get(cliente_id)
    if not cliente:
        return jsonify({"error": "Cliente no encontrado"}), 404

    cobrador = Usuario.query.get(cobrador_id)
    if not cobrador or cobrador.rol != 'cobrador':
        return jsonify({"error": "El usuario no existe o no tiene el rol de cobrador"}), 400
    
    saldo_pendiente = numero_cuota * valor_cuota
    total_deuda = monto_prestado + saldo_pendiente

    nuevo_prestamo = Prestamo(
        cliente_id=cliente_id,
        cobrador_id=cobrador_id,
        monto_prestado=monto_prestado,
        numero_cuota=numero_cuota,
        valor_cuota=valor_cuota,
        saldo_pendiente=saldo_pendiente,
        total_deuda=total_deuda
    )
    db.session.add(nuevo_prestamo)
    db.session.commit()

    return jsonify({"message": "Préstamo registrado con éxito", "id": nuevo_prestamo.id}), 201

@app.route('/clientes', methods=['GET'])
def obtener_todos_los_clientes():
    clientes = Cliente.query.all()
    
    resultado = [
        {
            "id": cliente.id,
            "nombre": cliente.nombre,
            "fecha_inicio": cliente.fecha_inicio.strftime('%Y-%m-%d'),
            "fecha_termino": cliente.fecha_termino.strftime('%Y-%m-%d'),
            "prestamos": [
                {
                    "id": prestamo.id,
                    "monto_prestado": prestamo.monto_prestado,
                    "numero_cuota": prestamo.numero_cuota,
                    "valor_cuota": prestamo.valor_cuota,
                    "valor_saldado": prestamo.valor_saldado,
                    "saldo_pendiente": prestamo.saldo_pendiente,
                    "total_deuda": prestamo.total_deuda,
                    "cobrador_id": prestamo.cobrador_id
                } for prestamo in cliente.prestamos
            ]
        } for cliente in clientes
    ]
    
    return jsonify(resultado)
@app.route('/cliente/<int:id>', methods=['GET'])
def obtener_cliente_con_prestamos(id):
    cliente = Cliente.query.get_or_404(id)
    
    resultado = {
        "id": cliente.id,
        "nombre": cliente.nombre,
        "fecha_inicio": cliente.fecha_inicio.strftime('%Y-%m-%d'),
        "fecha_termino": cliente.fecha_termino.strftime('%Y-%m-%d'),
        "prestamos": [
            {
                "id": prestamo.id,
                "monto_prestado": prestamo.monto_prestado,
                "numero_cuota": prestamo.numero_cuota,
                "valor_cuota": prestamo.valor_cuota,
                "valor_saldado": prestamo.valor_saldado,
                "saldo_pendiente": prestamo.saldo_pendiente,
                "total_deuda": prestamo.total_deuda,
                "cobrador_id": prestamo.cobrador_id
            } for prestamo in cliente.prestamos
        ]
    }
    
    return jsonify(resultado)


if __name__ == "__main__":
    app.run(debug=True, port=5002)