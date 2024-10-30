from flask import Flask, request, jsonify, session
from models import *
from config import *
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


# Rutas de la aplicación

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

# Rutas de Usuario
@app.route('/usuario', methods=['POST'])
def registrar_usuario():
    data = request.get_json()
    nombre_usuario = data.get('nombre_usuario')
    numero_identificacion = data.get('numero_identificacion')
    contraseña = generate_password_hash(data.get('contraseña'))
    rol = data.get('rol')

    if not all([nombre_usuario, numero_identificacion, contraseña, rol]):
        return jsonify({"error": "Todos los campos son obligatorios"}), 400

    nuevo_usuario = Usuario(
        nombre_usuario=nombre_usuario,
        numero_identificacion=numero_identificacion,
        contraseña=contraseña,
        rol=rol
    )
    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({"message": "Usuario registrado con éxito", "id": nuevo_usuario.id}), 201
# Ruta de login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    nombre_usuario = data.get('nombre_usuario')
    contraseña = data.get('contraseña')

    if not nombre_usuario or not contraseña:
        return jsonify({"error": "Nombre de usuario y contraseña son obligatorios"}), 400

    # Buscar usuario por nombre de usuario
    usuario = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()
    
    # Verificar si el usuario existe y la contraseña es correcta
    if usuario and check_password_hash(usuario.contraseña, contraseña):
        # Generar una sesión o token para el usuario
        session['user_id'] = usuario.id  # Configuración básica de sesión
        return jsonify({"message": "Inicio de sesión exitoso", "user_id": usuario.id}), 200
    else:
        return jsonify({"error": "Credenciales incorrectas"}), 401
# Rutas de Cliente
@app.route('/cliente', methods=['POST'])
def registrar_cliente():
    data = request.get_json()
    nombre = data.get('nombre')
    numero_identificacion = data.get('numero_identificacion')
    telefono = data.get('telefono')
    email = data.get('email')
    direccion = data.get('direccion')
    cobrador_id = data.get('cobrador_id')

    if not all([nombre, numero_identificacion, cobrador_id]):
        return jsonify({"error": "Nombre, identificación y cobrador son obligatorios"}), 400

    nuevo_cliente = Cliente(
        nombre=nombre,
        numero_identificacion=numero_identificacion,
        telefono=telefono,
        email=email,
        direccion=direccion,
        cobrador_id=cobrador_id
    )
    db.session.add(nuevo_cliente)
    db.session.commit()

    return jsonify({"message": "Cliente registrado con éxito", "id": nuevo_cliente.id}), 201

# Rutas de Préstamo
@app.route('/prestamo', methods=['POST'])
def registrar_prestamo():
    data = request.get_json()
    cliente_id = data.get('cliente_id')
    cobrador_id = data.get('cobrador_id')
    monto_prestado = data.get('monto_prestado')
    numero_cuota = data.get('numero_cuota')
    valor_cuota = data.get('valor_cuota')
    cuotas_saldadas = data.get('cuotas_saldadas', 0)
    fecha_inicio = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d')
    fecha_termino = datetime.strptime(data['fecha_termino'], '%Y-%m-%d')
    
    if not all([cliente_id, cobrador_id, monto_prestado, numero_cuota, valor_cuota, fecha_inicio, fecha_termino]):
        return jsonify({"error": "Todos los campos son obligatorios"}), 400

    valor_saldado = valor_cuota * cuotas_saldadas
    saldo_pendiente = numero_cuota * valor_cuota - valor_saldado
    total_deuda = valor_cuota * numero_cuota

    nuevo_prestamo = Prestamo(
        cliente_id=cliente_id,
        cobrador_id=cobrador_id,
        monto_prestado=monto_prestado,
        numero_cuota=numero_cuota,
        cuotas_saldadas=cuotas_saldadas,
        valor_cuota=valor_cuota,
        saldo_pendiente=saldo_pendiente,
        total_deuda=total_deuda,
        fecha_inicio=fecha_inicio,
        fecha_termino=fecha_termino,
    )
    db.session.add(nuevo_prestamo)
    db.session.commit()

    return jsonify({"message": "Préstamo registrado con éxito", "id": nuevo_prestamo.id}), 201

# Pagar Cuota
@app.route('/prestamo/pago/<int:prestamo_id>', methods=['POST'])
def pagar_cuota(prestamo_id):
    prestamo = Prestamo.query.get(prestamo_id)
    if not prestamo:
        return jsonify({"error": "Préstamo no encontrado"}), 404

    if prestamo.cuotas_saldadas >= prestamo.numero_cuota:
        return jsonify({"message": "Todas las cuotas ya han sido pagadas"}), 400

    prestamo.cuotas_saldadas += 1
    prestamo.saldo_pendiente -= prestamo.valor_cuota
    db.session.commit()

    return jsonify({"message": "Cuota pagada con éxito", "saldo_pendiente": prestamo.saldo_pendiente}), 200

# Obtener Clientes por Cobrador
@app.route('/cobrador/clientes/<int:cobrador_id>', methods=['GET'])
def obtener_clientes_por_cobrador(cobrador_id):
    cobrador = Usuario.query.get(cobrador_id)
    if not cobrador or cobrador.rol != 'cobrador':
        return jsonify({"error": "Cobrador no encontrado o no tiene el rol adecuado"}), 404

    clientes = Cliente.query.filter_by(cobrador_id=cobrador_id).all()
    clientes_data = []
    for cliente in clientes:
        cliente_info = {
            "id": cliente.id,
            "nombre": cliente.nombre,
            "numero_identificacion": cliente.numero_identificacion,
            "telefono": cliente.telefono,
            "email": cliente.email,
            "direccion": cliente.direccion,
            "prestamos": []
        }
        
        for prestamo in cliente.prestamos:
            cliente_info["prestamos"].append({
                "id": prestamo.id,
                "monto_prestado": prestamo.monto_prestado,
                "numero_cuota": prestamo.numero_cuota,
                "valor_cuota": prestamo.valor_cuota,
                "valor_saldado": prestamo.valor_cuota * prestamo.cuotas_saldadas,
                "saldo_pendiente": prestamo.saldo_pendiente,
                "total_deuda": prestamo.total_deuda,
                "fecha_inicio": prestamo.fecha_inicio.strftime('%Y-%m-%d'),
                "fecha_termino": prestamo.fecha_termino.strftime('%Y-%m-%d')
            })
        
        clientes_data.append(cliente_info)

    return jsonify({
        "cobrador": {
            "id": cobrador.id,
            "nombre_usuario": cobrador.nombre_usuario,
            "numero_identificacion": cobrador.numero_identificacion,
            "rol": cobrador.rol
        },
        "clientes": clientes_data
    }), 200

if __name__ == "__main__":
    app.run(debug=True, port=5002)