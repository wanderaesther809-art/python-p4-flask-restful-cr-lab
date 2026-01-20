#!/usr/bin/env python3

import os
from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource

# Import your db and models
from models import db, Plant

# --- DATABASE PATH FIX ---
# This finds the absolute path of the folder this file is in (the 'server' folder)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, 'app.db')

app = Flask(__name__)

# Force the URI to point exactly to server/app.db
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = True

# Initialize Migrate and DB
migrate = Migrate(app, db)
db.init_app(app)

# Initialize the API
api = Api(app)

class Plants(Resource):
    def get(self):
        plants = [p.to_dict() for p in Plant.query.all()]
        return make_response(jsonify(plants), 200)

    def post(self):
        data = request.get_json()
        try:
            new_plant = Plant(
                name=data.get('name'),
                image=data.get('image'),
                price=data.get('price')
            )
            db.session.add(new_plant)
            db.session.commit()
            return make_response(jsonify(new_plant.to_dict()), 201)
        except Exception:
            db.session.rollback()
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

class PlantByID(Resource):
    def get(self, id):
        plant = Plant.query.filter_by(id=id).first()
        if plant:
            return make_response(jsonify(plant.to_dict()), 200)
        return make_response(jsonify({"error": "Plant not found"}), 404)

    def delete(self, id):
        plant = Plant.query.filter_by(id=id).first()
        if plant:
            db.session.delete(plant)
            db.session.commit()
            return make_response('', 204)
        return make_response(jsonify({"error": "Plant not found"}), 404)

# Register the Resources
api.add_resource(Plants, '/plants')
api.add_resource(PlantByID, '/plants/<int:id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)