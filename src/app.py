"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os, json
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Favorites
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
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

@app.route('/users', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

#Todos los usuarios
@app.route('/user', methods=['GET'])
def get_all_users():
    users = User.query.all()
    if len(users) < 1:
        return jsonify({"msg": "not found"}), 404
    serialized_users = list(map(lambda x: x.serialize(), users))
    return serialized_users, 200

#Usuario específico
@app.route('/user/<int:user_id>', methods=['GET'])
def get_one_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"msg": f"user with id {user_id} not found"}), 404
    serialized_user = user.serialize()
    return serialized_user, 200

#Todos los character
@app.route('/character', methods=['GET'])
def get_all_character():
    characters = Character.query.all()
    if len(characters) < 1:
        return jsonify({"msg": "not found"}), 404
    serialized_characters = list(map(lambda x: x.serialize(), characters))
    return serialized_characters, 200



#Character específico
@app.route('/character/<int:character_id>', methods=['GET'])
def get_one_character(character_id):
    character = Character.query.get(character_id)
    if character is None:
        return jsonify({"msg": f"user with id {character_id} not found"}), 404
    serialized_character = character.serialize()
    return serialized_character, 200

#Todas las planetas
@app.route('/planet', methods=['GET'])
def get_all_planet():
    planets = Planet.query.all()
    if len(planets) < 1:
        return jsonify({"msg": "not found"}), 404
    serialized_planets = list(map(lambda x: x.serialize(), planets))
    return serialized_planets, 200

#Planet específico
@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_one_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"msg": f"user with id {planet_id} not found"}), 404
    serialized_planet = planet.serialize()
    return serialized_planet, 200


@app.route('/user/favorites', methods=['GET'])
def get_user_favorites():
    CURRENT_USER_ID = 1  

    # Obtener el usuario actual
    user = User.query.get(CURRENT_USER_ID)
    
    if user is None:
        return jsonify({"msg": "User not found"}), 404

    # Consultar todos los favoritos del usuario actual
    favorites = Favorites.query.filter_by(user_id=CURRENT_USER_ID).all()

    if len(favorites) == 0:
        return jsonify({"msg": "No favorites found"}), 404

    # Serializar los favoritos
    serialized_favorites = []
    for favorite in favorites:
        serialized_favorite = {
            "id": favorite.id,
            "user_id": favorite.user_id,
            "character": Character.query.get(favorite.character_id).serialize(),
            "planet": Planet.query.get(favorite.planet_id).serialize()
        }
        serialized_favorites.append(serialized_favorite)

    return jsonify(serialized_favorites), 200



# Crear un usuario
@app.route('/user', methods=['POST'])
def create_one_user():
    body = json.loads(request.data)
    new_user = User(
        email = body["email"],
        password = body["password"],
        is_active = True
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"msg": "user created succesfull"}), 200

# Crear un character
@app.route('/character', methods=['POST'])
def create_one_character():
    body = json.loads(request.data)
    new_character = Character(
        name = body["name"],
        gender = body["gender"],
        eyes_color = body["eyes_color"]
    )
    db.session.add(new_character)
    db.session.commit()
    return jsonify({"msg": "character created succesfull"}), 200

# Crear un Planetas
@app.route('/planet', methods=['POST'])
def create_one_planet():
    body = json.loads(request.data)
    new_planet = Planet(
        name = body["name"],
        clima = body["clima"],
        temperatura = body["temperatura"]
    )
    db.session.add(new_planet)
    db.session.commit()
    return jsonify({"msg": "planet created succesfull"}), 200

# Delete user
@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_one_user(user_id):
    delete_user = User.query.get(user_id)
    db.session.delete(delete_user)
    db.session.commit()
    return jsonify({"msg": "user deleted succesfull"}), 200

# Delete character
@app.route('/character/<int:character_id>', methods=['DELETE'])
def delete_one_character(character_id):
    delete_character = Character.query.get(character_id)
    db.session.delete(delete_character)
    db.session.commit()
    return jsonify({"msg": "character deleted succesfull"}), 200

# Delete planet
@app.route('/planet/<int:planet_id>', methods=['DELETE'])
def delete_one_planet(planet_id):
    delete_planet = Planet.query.get(planet_id)
    db.session.delete(delete_planet)
    db.session.commit()
    return jsonify({"msg": "planet deleted succesfull"}), 200



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
