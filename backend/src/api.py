import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db, db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES



'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def retrieve_drinks():
    try:
        drinks = Drink.query.all()
    except Exception as e:
        print(e)
        db.session.rollback()
        abort(422)
    finally:
        db.session.close()
        return jsonify({
            "success": True, 
            "status_code": 200,
            "drinks": [drink.short() for drink in drinks]
        })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def retrieve_drinks_detail(jwt):
    try:
        drinks = Drink.query.all()
    except Exception as e:
        print(e)
        db.session.rollback()
        abort(422)
    finally:
        db.session.close()
        return jsonify({
            "success": True,
            "status_code": 200,
            "drinks": [drink.long() for drink in drinks]
        })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def insert_drinks(jwt):
    body = request.get_json()
    title =  body.get('title', None)
    recipe = body.get('recipe', None) 
    if not title or not recipe:
        abort(400)
    try:
        new_drink = Drink(
            title=title,
            recipe=json.dumps(recipe)
        )
        new_drink.insert()
    except Exception as e:
        print(e)
        db.session.rollback()
        return abort(422)
    finally:
        db.session.close()
        return jsonify({
            "success": True,
            "drinks":  [new_drink.long()]
        })


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<edit_id>', methods = ['PATCH'])
@requires_auth('patch:drinks')
def edit_drinks_detail(jwt, edit_id):
    try:
        drink = Drink.query.filter_by(id=edit_id).one_or_none()
        if not drink:
            abort(404)
        body = request.get_json()
        title =  body.get('title', drink.title)
        recipe = body.get('recipe', None)
        if recipe:
            drink.recipe = json.dumps(recipe)
        drink.title = title
        drink.update()
    except Exception as e:
        print(e)
        abort(422)
        db.session.rollback()
    finally:
        db.session.close()
        return jsonify({
            "success": True, 
            "drinks": [drink.long()]
        })
'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<delete_id>', methods = ['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks_detail(jwt, delete_id):
    try:
        drink = Drink.query.filter_by(id=delete_id).one_or_none()
        if not drink:
            abort(404)
        drink.delete()
    except Exception as e:
        print(e)
        abort(422)
        db.session.rollback()
    finally:
        db.session.close()
        return jsonify({
            "success": True, 
            "delete": delete_id
        })


## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404
'''
'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def handle_not_found(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
