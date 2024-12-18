from flask import Flask, request, jsonify, session
from models import *
from config import *
from sqlalchemy.orm import joinedload 
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
    numero_identificacion = data.get('numero_identificacion')
    contraseña = data.get('contraseña')

    if not numero_identificacion or not contraseña:
        return jsonify({"error": "Número de identificación y contraseña son obligatorios"}), 400

    # Buscar usuario por número de identificación
    usuario = Usuario.query.filter_by(numero_identificacion=numero_identificacion).first()
    
    # Verificar si el usuario existe y la contraseña es correcta
    if usuario and check_password_hash(usuario.contraseña, contraseña):
        # Generar una sesión o token para el usuario
        session['user_id'] = usuario.id  # Configuración básica de sesión
        return jsonify({"status": "ok", "user_id": usuario.id, "nombre": usuario.nombre_usuario}), 200
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

    return jsonify({"status": 200, "message": "Cliente registrado con éxito", "id": nuevo_cliente.id}), 201

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

    return jsonify({"status": 200, "message": "Préstamo registrado con éxito", "id": nuevo_prestamo.id}), 201

# Pagar Cuota



# Guardar un nuevo pago
@app.route('/pago', methods=['POST'])
def registrar_pago():
    data = request.get_json()
    prestamo_id = data.get('prestamo_id')
    monto_abonado = data.get('monto_abonado')

    # Validar datos obligatorios
    if not prestamo_id or not monto_abonado:
        return jsonify({'error': 'Los campos prestamo_id y monto_abonado son obligatorios'}), 400

    # Buscar el préstamo asociado
    prestamo = Prestamo.query.get(prestamo_id)
    if not prestamo:
        return jsonify({'error': 'El préstamo no existe'}), 404

    # Calcular saldo restante
    nuevo_saldo_pendiente = prestamo.saldo_pendiente - monto_abonado
    if nuevo_saldo_pendiente < 0:
        return jsonify({'error': 'El monto abonado no puede ser mayor que el saldo pendiente'}), 400

    # Registrar el pago
    nuevo_pago = Pago(
        prestamo_id=prestamo_id,
        fecha_pago=datetime.utcnow(),
        monto_abonado=monto_abonado,
        saldo_restante=nuevo_saldo_pendiente
    )
    db.session.add(nuevo_pago)

    # Actualizar el saldo pendiente y estado del préstamo
    prestamo.saldo_pendiente = nuevo_saldo_pendiente
    if nuevo_saldo_pendiente == 0:
        prestamo.estado = 'saldado'
        prestamo.fecha_saldado = datetime.utcnow()

    db.session.commit()

    return jsonify({'mensaje': 'Pago registrado exitosamente', 'pago': {
        'id': nuevo_pago.id,
        'prestamo_id': nuevo_pago.prestamo_id,
        'fecha_pago': nuevo_pago.fecha_pago,
        'monto_abonado': nuevo_pago.monto_abonado,
        'saldo_restante': nuevo_pago.saldo_restante
    }}), 201

# Obtener todos los pagos
@app.route('/pagos', methods=['GET'])
def obtener_todos_los_pagos():
    pagos = Pago.query.all()
    resultados = []
    for pago in pagos:
        resultados.append({
            'id': pago.id,
            'prestamo_id': pago.prestamo_id,
            'fecha_pago': pago.fecha_pago,
            'monto_abonado': pago.monto_abonado,
            'saldo_restante': pago.saldo_restante
        })
    return jsonify(resultados), 200

# Obtener pagos de un préstamo específico
@app.route('/prestamo/pagos/<int:prestamo_id>', methods=['GET'])
def obtener_pagos_por_prestamo(prestamo_id):
    prestamo = Prestamo.query.get(prestamo_id)
    if not prestamo:
        return jsonify({'error': 'El préstamo no existe'}), 404

    pagos = Pago.query.filter_by(prestamo_id=prestamo_id).all()
    resultados = []
    for pago in pagos:
        resultados.append({
            'id': pago.id,
            'fecha_pago': pago.fecha_pago,
            'monto_abonado': pago.monto_abonado,
            'saldo_restante': pago.saldo_restante
        })
    return jsonify({
        'prestamo_id': prestamo_id,
        'pagos': resultados
    }), 200

#------------------------ prestamos ------------------------------#
@app.route('/prestamos-pagos', methods=['GET'])
def obtener_prestamos_con_pagos():
    prestamos = Prestamo.query.all()
    resultados = []

    for prestamo in prestamos:
        pagos = Pago.query.filter_by(prestamo_id=prestamo.id).all()
        lista_pagos = [
            {
                'id': pago.id,
                'fecha_pago': pago.fecha_pago,
                'monto_abonado': pago.monto_abonado,
                'metodo_pago': pago.metodo_pago,
                'saldo_restante': pago.saldo_restante
            } for pago in pagos
        ]

        resultados.append({
            'id': prestamo.id,
            'cliente_id': prestamo.cliente_id,
            'cobrador_id': prestamo.cobrador_id,
            'monto_prestado': prestamo.monto_prestado,
            'numero_cuota': prestamo.numero_cuota,
            'valor_cuota': prestamo.valor_cuota,
            'cuotas_saldadas': prestamo.cuotas_saldadas,
            'saldo_pendiente': prestamo.saldo_pendiente,
            'total_deuda': prestamo.total_deuda,
            'fecha_inicio': prestamo.fecha_inicio,
            'fecha_termino': prestamo.fecha_termino,
            'fecha_saldado': prestamo.fecha_saldado,
            'estado': prestamo.estado,
            'pagos': lista_pagos
        })

    return jsonify(resultados), 200

@app.route('/prestamos-pagos/<int:prestamo_id>', methods=['GET'])
def obtener_prestamo_con_pagos(prestamo_id):
    prestamo = Prestamo.query.get(prestamo_id)
    
    if not prestamo:
        return jsonify({'error': 'Préstamo no encontrado'}), 404

    pagos = Pago.query.filter_by(prestamo_id=prestamo_id).all()
    lista_pagos = [
        {
            'id': pago.id,
            'fecha_pago': pago.fecha_pago,
            'monto_abonado': pago.monto_abonado,
            'metodo_pago': pago.metodo_pago,
            'saldo_restante': pago.saldo_restante
        } for pago in pagos
    ]

    resultado = {
        'id': prestamo.id,
        'cliente_id': prestamo.cliente_id,
        'cobrador_id': prestamo.cobrador_id,
        'monto_prestado': prestamo.monto_prestado,
        'numero_cuota': prestamo.numero_cuota,
        'valor_cuota': prestamo.valor_cuota,
        'cuotas_saldadas': prestamo.cuotas_saldadas,
        'saldo_pendiente': prestamo.saldo_pendiente,
        'total_deuda': prestamo.total_deuda,
        'fecha_inicio': prestamo.fecha_inicio,
        'fecha_termino': prestamo.fecha_termino,
        'fecha_saldado': prestamo.fecha_saldado,
        'estado': prestamo.estado,
        'pagos': lista_pagos
    }

    return jsonify(resultado), 200

#------------------------------------- // -------------------------------#


@app.route('/prestamo/pago/<int:prestamo_id>', methods=['PUT'])
def pagar_cuota(prestamo_id):
    prestamo = Prestamo.query.get(prestamo_id)
    if not prestamo:
        return jsonify({"error": "Préstamo no encontrado"}), 404

    # Verificar si el préstamo ya está saldado
    if prestamo.cuotas_saldadas >= prestamo.numero_cuota:
        return jsonify({"message": "Todas las cuotas ya han sido pagadas"}), 400

    # Incrementar el número de cuotas saldadas y reducir el saldo pendiente
    prestamo.cuotas_saldadas += 1
    prestamo.saldo_pendiente -= prestamo.valor_cuota

    # Verificar si el préstamo ha sido completamente saldado
    if prestamo.cuotas_saldadas == prestamo.numero_cuota:
        prestamo.fecha_saldado = datetime.now()
        prestamo.estado = "saldado"

    db.session.commit()

    return jsonify({
        "status": 200,
        "message": "Cuota pagada con éxito",
        "saldo_pendiente": prestamo.saldo_pendiente,
        "estado": prestamo.estado,
        "fecha_saldado": prestamo.fecha_saldado
    }), 200



@app.route('/prestamo/abono/<int:prestamo_id>', methods=['POST'])
def abono_parcial(prestamo_id):
    data = request.get_json()
    monto_abono = data.get('monto_abono')

    if not monto_abono or monto_abono <= 0:
        return jsonify({"error": "Monto de abono inválido"}), 400

    prestamo = Prestamo.query.get(prestamo_id)
    if not prestamo:
        return jsonify({"error": "Préstamo no encontrado"}), 404

    # Verificar si el préstamo ya está completamente saldado
    if prestamo.saldo_pendiente <= 0:
        return jsonify({"message": "El préstamo ya ha sido completamente saldado"}), 400

    # Calcular el valor de cada cuota
    valor_cuota = prestamo.monto_prestado / prestamo.numero_cuota

    # Limitar el abono al saldo pendiente para evitar saldo negativo
    if monto_abono > prestamo.saldo_pendiente:
        monto_abono = prestamo.saldo_pendiente

    # Aplicar el abono al saldo pendiente
    prestamo.saldo_pendiente -= monto_abono

    # Calcular las cuotas completas basadas en el saldo pendiente restante
    cuotas_saldadas = int((prestamo.monto_prestado - prestamo.saldo_pendiente) / valor_cuota)
    prestamo.cuotas_saldadas = cuotas_saldadas

    # Verificar si el préstamo ha sido completamente saldado
    if prestamo.saldo_pendiente <= 0:
        prestamo.fecha_saldado = datetime.now()
        prestamo.estado = "saldado"

    db.session.commit()

    return jsonify({
        "status": 200,
        "message": "Abono registrado con éxito",
        "saldo_pendiente": prestamo.saldo_pendiente,
        "cuotas_saldadas": prestamo.cuotas_saldadas,
        "estado": prestamo.estado,
        "fecha_saldado": prestamo.fecha_saldado
    }), 200



# Obtener Clientes por Cobrador

@app.route('/clientes/prestamos/<int:cliente_id>', methods=['GET'])
def obtener_prestamos_cliente(cliente_id):
    cliente = Cliente.query.get(cliente_id)
    if not cliente:
        return jsonify({"error": "Cliente no encontrado"}), 404

    prestamos = [
        {
            "id": prestamo.id,
            "monto_prestado": prestamo.monto_prestado,
            "numero_cuota": prestamo.numero_cuota,
            "cuotas_saldadas": prestamo.cuotas_saldadas,
            "valor_cuota": prestamo.valor_cuota,
            "saldo_pendiente": prestamo.saldo_pendiente,
            "total_deuda": prestamo.total_deuda,
            "fecha_inicio": prestamo.fecha_inicio,
            "fecha_termino": prestamo.fecha_termino,
            "fecha_saldado": prestamo.fecha_saldado,
            "estado": prestamo.estado
        }
        for prestamo in cliente.prestamos
    ]

    return jsonify({
        "cliente": {
            "id": cliente.id,
            "nombre": cliente.nombre
        },
        "prestamos": prestamos
    }), 200

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
        
        # Añadir información de cada préstamo del cliente
        for prestamo in cliente.prestamos:
            cliente_info["prestamos"].append({
                "id": prestamo.id,
                "monto_prestado": prestamo.monto_prestado,
                "numero_cuota": prestamo.numero_cuota,
                "valor_cuota": prestamo.valor_cuota,
                "valor_saldado": prestamo.valor_cuota * prestamo.cuotas_saldadas,
                "saldo_pendiente": prestamo.saldo_pendiente,
                "total_deuda": prestamo.total_deuda,
                "cuotas_saldadas": prestamo.cuotas_saldadas,
                "fecha_inicio": prestamo.fecha_inicio.strftime('%Y-%m-%d'),
                "fecha_termino": prestamo.fecha_termino.strftime('%Y-%m-%d'),
                "fecha_saldado": prestamo.fecha_saldado.strftime('%Y-%m-%d') if prestamo.fecha_saldado else None,
                "estado": prestamo.estado
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

@app.route('/cliente/<int:cliente_id>', methods=['GET'])
def obtener_cliente_con_prestamos(cliente_id):
    cliente = Cliente.query.options(joinedload(Cliente.prestamos)).filter_by(id=cliente_id).first() # type: ignore

    if not cliente:
        return jsonify({"error": "Cliente no encontrado"}), 404

    # Estructura de respuesta con los datos del cliente y sus préstamos
    cliente_data = {
        "id": cliente.id,
        "nombre": cliente.nombre,
        "numero_identificacion": cliente.numero_identificacion,
        "telefono": cliente.telefono,
        "email": cliente.email,
        "direccion": cliente.direccion,
        "prestamos": []
    }

    # Agregar los préstamos del cliente con su estado actual
    for prestamo in cliente.prestamos:
        cliente_data["prestamos"].append({
            "id": prestamo.id,
            "monto_prestado": prestamo.monto_prestado,
            "numero_cuota": prestamo.numero_cuota,
            "valor_cuota": prestamo.valor_cuota,
            "valor_saldado": prestamo.valor_cuota * prestamo.cuotas_saldadas,
            "saldo_pendiente": prestamo.saldo_pendiente,
            "cuotas_saldadas": prestamo.cuotas_saldadas,
            "total_deuda": prestamo.total_deuda,
            "estado": prestamo.estado,  # Activo o Saldado
            "fecha_inicio": prestamo.fecha_inicio.strftime('%Y-%m-%d'),
            "fecha_termino": prestamo.fecha_termino.strftime('%Y-%m-%d')
        })

    return jsonify(cliente_data), 200

if __name__ == "__main__":
    app.run(debug=True, port=5002)