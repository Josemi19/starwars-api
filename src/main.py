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

@app.route('/user/<int:user_id>/favorites/<category>/<int:name_id>', methods = ['POST'])
def add_favs(category, name_id, user_id):
    body = request.json
    user = body.get("user_id", None)
    category = body.get("category", None)
    name = body.get("name_id", None)
    if category and name and user is not None:
        if request.method == 'POST':
            user = Usuario.query.filter_by(id = user_id).first()
            if user is not None:
                if category == "Planeta" or category == "Personaje":
                    if category == "Planeta":
                        name = Planeta.query.filter_by(id = name_id).first()
                        if name is not None:                                           # AGREGAR PLANETA
                            fav = Favorito.query.filter_by(name = name.name).first()
                            if fav is not None:
                                return jsonify({
                                    "msg":"Already exist"
                                })
                            else:
                                try:
                                    new_fav = Favorito(
                                        usuario_id = user.id,
                                        category = category,
                                        name = name.name
                                    )
                                    db.session.add(new_fav)
                                    db.session.commit()
                                    return "Agregado", 201
                                except Exception as error:
                                    db.session.rollback()
                                    return jsonify(error.args), 500
                        else:
                            return jsonify({
                                "msg": "Planeta no existe"
                            }), 404
                    if category == "Personaje":                     # AGREGAR PERSONAJE
                        name = Personaje.query.filter_by(id = name_id).first()
                        if name is not None:
                            fav = Favorito.query.filter_by(name = name.name).first()
                            if fav is not None:
                                return jsonify({
                                    "msg":"Already exist"
                                })
                            else:
                                try:
                                    new_fav = Favorito(
                                        usuario_id = user.id,
                                        category = category,
                                        name = name.name
                                    )
                                    db.session.add(new_fav)
                                    db.session.commit()
                                    return "Agregado", 201
                                except Exception as error:
                                    db.session.rollback()
                                    return jsonify(error.args), 500
                        else:
                            return jsonify({
                                "msg": "Planeta no existe"
                            }), 404
                else:
                    return jsonify({
                        "msg":"Category must be Planeta or Personaje"
                    }), 404
            else:
                return jsonify({
                    "msg":"Usuario no existe"
                }), 404
    else:
        return jsonify({
            "msg": "Something Happened"
        })

@app.route('/favorites/<int:fav_id>', methods = ['DELETE'])
def delete_favs(fav_id):
    body = request.json
    fav = body.get("fav_id", None)
    if fav is not None:
        fav = Favorito.query.filter_by(id = fav_id).first()
        if fav is not None:
            try:
                db.session.delete(fav)
                db.session.commit()
                return "Eliminado", 200
            except Exception as error:
                db.session.rollback()
                return jsonify(error.args), 500
        else:
            return jsonify({
                "msg": "Favorito no existe"
            }), 404
    else:
        return jsonify({
            "msg":"Something Happened"
        }), 400

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
