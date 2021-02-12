from flask import Flask, request, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash

from flask_mail import Mail, Message
from utils import random_token

from models import *
from config import *


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


@app.route('/signup', methods=['POST'])
def signup_post():
    email = request.json['email']
    name = request.json['name']
    password = request.json['password']
    admin=False,
    confirmed=False,
    confirmed_on=datetime.datetime.now()
    token_confirmations = random_token()

    user = User.query.filter_by(email=email).first()

    if user:
        return jsonify ({'mensaje' : 'Ya te encuentras registrado'})

    new_user = User(email=email, name=name, confirmed=False, token_confirmations=token_confirmations,
                    password=generate_password_hash(password, method='sha256'))



    msg = Message('Codigo de confirmacion', sender = 'mnsneptuno@gmail.com', recipients = [email])
    msg.body = "Su codigo de confirmacion es:" + str(token_confirmations)
    mail.send(msg)

    db.session.add(new_user)
    db.session.commit()

    return jsonify ({'mensaje' : 'Confirma el codigo enviado para ingresar'})


@app.route('/confirmed/<id>', methods=['PUT'])
def confirmed(id):
      
      token_confirmations = request.json['token_confirmations']
      

      token = User.query.filter_by(token_confirmations=token_confirmations).first()

      if not token:
            return jsonify ({'mensaje' : 'verifica tu token en el email'})


      user = User.query.get(id)
      confirmed = request.json['confirmed']
      user.confirmed = confirmed
      db.session.commit() 
      return jsonify ({'mensaje' : 'Registro exitoso'})


     
      
@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))


@app.route('/login', methods=['POST'])
def login():
    email = request.json['email']
    password = request.json['password']
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email, confirmed=True).first()

    if not user and not check_password_hash(user.password, password):
        return jsonify ({'mensaje' : 'verifica tu correo y contraseña'})

    
    login_user(user, remember=remember)
    db.session.close()

    return jsonify ({'mensaje' : 'Login exitoso'})


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify ({'mensaje' : 'Sesion finalizada'})



@app.route('/users', methods=['GET'])
@login_required
def get_users():
  all_users = User.query.all()
  result = users_schema.dump(all_users)
  return jsonify(result)


@app.route('/users/<id>', methods=['GET'])
@login_required
def get_user(id):
  user = User.query.get(id)
  return user_schema.jsonify(user)
  

@app.route('/users/<id>', methods=['PUT'])
@login_required
def update_users(id):
  user = User.query.get(id)


  email = request.json['email']
  password = request.json['password']
  name = request.json['name']
  identification = request.json['identification']
  address = request.json['address']
  contact = request.json['contact']
  services = request.json['services']


  user.email = email
  user.password = password
  user.name = name
  user.identification = identification
  user.address = address
  user.contact = contact
  user.services = services

  db.session.commit()
  return jsonify ({'mensaje' : 'usuario actualizado corectamente'})



@app.route('/observations', methods=['POST'])
@login_required
def create_task():
  title = request.json['title']
  description = request.json['description']
  user_id = request.json['user_id']

  new_observation= Observation(title, description, user_id)

  db.session.add(new_observation)
  db.session.commit()

  return jsonify ({'mensaje' : 'Tarea registrada con exito'})




@app.route('/observations', methods=['GET'])
@login_required
def get_observations():
  
  all_observations = Observation.query.join(User, User.id == Observation.user_id).add_columns(Observation.id, Observation.title, Observation.description, User.name)
  result = observations_schema.dump(all_observations)
  return jsonify(result)

@app.route('/user-observations/<id>', methods=['GET'])
@login_required
def get_observations_user(id):
  
  all_observations = Observation.query.join(User, User.id == Observation.user_id).add_columns(Observation.id, Observation.title, Observation.description, User.name).filter(User.id == id)
  result = observations_schema.dump(all_observations)
  return jsonify(result)

@app.route('/observations/<id>', methods=['GET'])
@login_required
def get_observation(id):
  observation = Observation.query.get(id)
  return observation_schema.jsonify(observation)


@app.route('/observations/<id>', methods=['PUT'])
@login_required
def update_observation(id):
  observation = observation.query.get(id)

  title = request.json['title']
  description = request.json['description']

  observation.title = title
  observation.description = description

  db.session.commit()

  return jsonify ({'mensaje' : 'se ha actializado correctamente tu tarea' })


@app.route('/observations/<id>', methods=['DELETE'])
@login_required
def delete_observation(id):
  observation = observation.query.get(id)
  db.session.delete(task)
  db.session.commit()
  return jsonify ({'mensaje' : 'se ha eliminado correctamente tu tarea' })


if __name__ == "__main__":
    app.run(debug=True, port=5002)