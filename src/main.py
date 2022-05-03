"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""

import json
import os
import re
from urllib import response
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import Favorito, Personaje, Planeta, db, Usuario
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/users')
def handle_users():
    
    users = Usuario.query.all()
    users = list(map(lambda user: user.serialize(), users))
    return jsonify(users), 200

@app.route('/people')
def handle_people():

    people = Personaje.query.all()
    people = list(map(lambda person: person.serialize(), people))
    return jsonify(people), 200

@app.route('/people/<int:people_id>')
def handle_people_id(people_id):

    person = Personaje.query.filter_by(id = people_id).first()
    if person is not None:
        return jsonify(person.serialize()), 200
    else:
        return jsonify({
            "msg": "Not Found"
        }), 404

@app.route('/planets')
def handle_planets():

    planets = Planeta.query.all()
    planets = list(map(lambda planet: planet.serialize(), planets))
    return jsonify(planets), 200

@app.route('/planets/<int:planet_id>')
def handle_planets_id(planet_id):

    planet = Planeta.query.filter_by(id= planet_id).first()
    if planet is not None:
        return jsonify(planet.serialize()), 200
    else:
        return jsonify({
            "msg": "Not Found"
        }), 404

@app.route('/users/<int:user_id>/favorites')
def handle_favs(user_id):
    user = Usuario.query.filter_by(id = user_id).first()
    if user is not None:
        favoritos = Favorito.query.filter_by(usuario_id = user_id)
        favoritos = list(map(lambda favorito: favorito.serialize(), favoritos))
        return jsonify(favoritos), 200
    else:
        return jsonify({
            "msg":"Not Found"
        }), 404

@app.route('/users/<int:user_id>/favorites/people/<int:people_id>', methods = ['POST', 'DELETE'])
def add_people(user_id, people_id):
    body = request.json
    user = body.get("usuario_id", None)
    person = body.get("personaje_id", None)
    if user and person is not None:
        if request.method == 'POST':  #METODO POST
            user = Usuario.query.filter_by(id = user_id).first()
            if user is not None:
                person = Personaje.query.filter_by(id = people_id).first()
                if person is not None:
                    fav = Favorito.query.filter_by(personaje_id = people_id).first()
                    if fav is not None:
                        return jsonify({
                            "msg":"Already exist"
                        })
                    else:
                        try:
                            new_favorite = Favorito(
                                usuario_id = user.id,
                                personaje_id = person.id
                            )
                            db.session.add(new_favorite)
                            db.session.commit()
                            return f"Agregado {person.id}", 200
                        except Exception as error:
                            db.session.rollback()
                            return jsonify(error.args), 500
                else:
                    return jsonify({
                        "msg":"Person doesn't exist"
                    })
            else:
                return jsonify({
                        "msg":"User doesn't exist"
                })
        if request.method == 'DELETE':  # METODO DELETE
            user = Usuario.query.filter_by(id = user_id).first()
            if user is not None:
                    fav = Favorito.query.filter_by(personaje_id = people_id).first()
                    if fav is not None:
                        try:
                            delete_favorite = Favorito(
                                usuario_id = user.id,
                                personaje_id = person.id
                            )
                            db.session.delete(delete_favorite)
                            db.session.commit()
                            return f"Eliminado {person}", 200
                        except Exception as error:
                            db.session.rollback()
                            return jsonify(error.args), 500
                    else:
                        return jsonify({
                            "msg":"Is not on the list"
                        })
            else:
                return jsonify({
                        "msg":"User doesn't exist"
                })
    else:
        return jsonify({
            "msg":"Something happened"
        })

    
    return "hola"



@app.route('/favorites/planets/<int:id>', methods = ['POST', 'DELETE'])
def add_planets(id):
    if request.method == 'POST':
        response = {
            "msg": f'Agregar este planeta {id}'
        }
    if request.method == 'DELETE':
        response = {
            "msg": f'Eliminar este planeta {id}'
        }
    return jsonify(response), 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
