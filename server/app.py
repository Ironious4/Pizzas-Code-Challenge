#!/usr/bin/env python3

from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route('/restaurants', methods=['GET'])
def restaurants():
    restaurants=[restaurant.to_dict() for restaurant in Restaurant.query.all()]

    response=make_response(
        restaurants,
        200
    )

    return response

@app.route('/restaurants/<int:id>', methods=['GET'])
def restaurant_by_id(id):
    restaurant=Restaurant.query.get(id)
    if restaurant is None:
        return {"error":"Restaurant not found"}, 404

    return jsonify({
        "id": restaurant.id,
        "name": restaurant.name,
        "address": restaurant.address,
        "restaurant_pizzas": [{
            "pizza_id": rp.pizza_id,
            "price": rp.price,
            "pizza_name": rp.pizza.name,  
            "pizza_ingredients": rp.pizza.ingredients
        } for rp in restaurant.restaurant_pizzas]
    }), 200

@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant=Restaurant.query.get(id)

    if not restaurant:
        return {"error":"Restaurant not found"}, 404

    db.session.delete(restaurant)
    db.session.commit()

    return '', 204


@app.route('/pizzas', methods=['GET'])
def pizzas():
    pizzas=[pizza.to_dict() for pizza in Pizza.query.all()]

    response=make_response(
        pizzas,
        200
    )

    return response


@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()

    price=int(data.get('price'))
    restaurant_id=data.get('restaurant_id')
    pizza_id=data.get('pizza_id')

    if not price or price < 1 or price > 30:
        return {"errors":["validation errors"]}, 400


    restaurant_pizza = RestaurantPizza(
        price=price,
        pizza_id=pizza_id,
        restaurant_id=restaurant_id
    )

    db.session.add(restaurant_pizza)
    db.session.commit()

    return jsonify({
        "id": restaurant_pizza.id,
        "price": restaurant_pizza.price,
        "pizza_id": restaurant_pizza.pizza_id,
        "restaurant_id": restaurant_pizza.restaurant_id,
        "pizza": {
            "id": restaurant_pizza.pizza.id,
            "name": restaurant_pizza.pizza.name,
            "ingredients": restaurant_pizza.pizza.ingredients
        },
        "restaurant": {
            "id": restaurant_pizza.restaurant.id,
            "name": restaurant_pizza.restaurant.name,
            "address": restaurant_pizza.restaurant.address
        }
    }), 201

    



if __name__ == '__main__':
    app.run(port=5555, debug=True)
