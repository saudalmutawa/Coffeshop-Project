import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES

@app.route('/drinks')
def get_drinks():

    drinks= Drink.query.order_by(Drink.id).all()
    if not drinks:
        abort(404)
    shortdrinks=[]
    for drink in drinks:
        shortdrinks.append(drink.short())

    return jsonify({
        "success":True,
        "drinks":shortdrinks
    }),200


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drink_details(jwt):
    try: 
        drinks = Drink.query.order_by(Drink.id).all()
        if not drinks:
            abort(404)
        longdrinks=[]
        for drink in drinks:
            longdrinks.append(drink.long())

        return jsonify({
                        "success":True,
                        "drinks":longdrinks
            }),200

    except:
        abort(404)

@app.route('/drinks',methods=['POST'])
@requires_auth('post:drinks')
def post_drink(jwt):
    try:
        
        body = request.get_json()

        d_title = body["title"]

        d_recipe=[]

        recipe=body["recipe"]

        d_recipe.append(recipe) #adding the dict into a list

        drink = Drink(title=d_title,recipe=json.dumps(d_recipe))  # json.dumps to convert single quote to double

        drink.insert()
        longdrink=[]
        longdrink.append(drink.long())

        return jsonify({
            "success":True,
            "drinks":longdrink
        }),200
    except:
        abort(400)

@app.route('/drinks/<id>',methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(jwt,id):
    try:
        body = request.get_json()

        if not id :
            abort(404)

        drink = Drink.query.filter(Drink.id==id).one_or_none()

        if drink is None:
            abort(404)

        if 'title' in body:
            d_title = body['title']
            drink.title=d_title        

        recipe={}
        if 'recipe' in body:
            recipe=body['recipe']
            d_recipe=[]
            d_recipe.append(recipe)
            drink.recipe=json.dumps(d_recipe)

        drink.update()
        longdrink=[]
        longdrink.append(drink.long())

        return jsonify({
            'success':True,
            'drinks':longdrink
        }),200
    except:
        abort(422)

@app.route('/drinks/<id>',methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(jwt,id):
    try:
        if not id:
            abort(404)

        drink = Drink.query.filter(Drink.id==id).one_or_none()

        if not drink:
            abort(404)

        drink.delete()
        return jsonify({
            'success':True,
            'drinks':id
        }),200
    except:
        abort(400)

# Error Handling

@app.errorhandler(400)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success":False,
        "error":404,
        "message":"resource not found"
    }),404

@app.errorhandler(AuthError)
def handle_auth_error(error):
    return jsonify({
        "success":False,
        "error":error.status_code,
        "message":error.error['description']    
    }),error.status_code

# https://udacity-coffeshop1.us.auth0.com/authorize?audience=dev&response_type=token&client_id=smAOVeHdNfIxNQy0pmcHlEDoX3JZpPvY&redirect_uri=https://127.0.0.1:8100