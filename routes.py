from weakref import WeakKeyDictionary
from flask import request, jsonify
from marshmallow.fields import Email
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import jwt
from datetime import datetime, timedelta


# from flask_login import User

from subFiles.config import app, bcrypt
from subFiles.model import db, profile, friend, drink, add_on, group_order, member
from subFiles.marsh import ma, ProfileSchema, DrinkSchema, AddOnSchema, FriendSchema, GroupOrderSchema, MembersSchema
from subFiles.marsh import profile_schema, drink_schema, addOn_schema, friend_schema, groupOrder_schema, member_schema
from subFiles.marsh import profiles_schema, drinks_schema, addOns_schema, friends_schema, groupOrders_schema, members_schema



# initializer examples for each data model
#    profile(username, email, password): relationship backref Names: (group_order: owner, drink: creator, friend: user_id )

#    friend(friend_username, friend_id, user_id): 

#    drink(name, is_hot, bean_type, level_of_roast, drink_type, creamer_type, sugar_type, milk_type, drink_location, profile_id): 
#   relationship backref Names: (add_on: add_on)

#    add_on(creamer_level, number_of_sugar_bags, milk_texture, milk_level, extra_comments):

#    group_order(order_location, order_time, is_admin): relationship backref Names: (member: member )

#    member(name):
#



def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.json['token']
        if not token:
            return jsonify({'message' : 'Token is missing!'}), 403
        
        try:
            print(token)
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except:
            return jsonify({'message' : 'Token is invalid'}), 403
        
        return func(*args, **kwargs)
    return decorated


#Sign Up a user
@app.route('/signUp', methods=['POST'])
def add_user():

    username = request.json['username']
    first_name = request.json['first_name']
    last_name = request.json['last_name']
    hashed_password = bcrypt.generate_password_hash(request.json['password']).decode('utf-8')
    email = request.json['email']

    existing_email = profile.query.filter_by(email=email).first()
    existing_username = profile.query.filter_by(username=username).first()  
    
    if not existing_email and not existing_username:
        new_user = profile(username,first_name, last_name, email, hashed_password)     
        db.session.add(new_user)
        db.session.commit()
        return profile_schema.jsonify(new_user)
    
    if existing_email: 
        return {'message': 'Email is already in use.'}
    
    if existing_username: 
        return {'message': 'Username is already in use.'}
    
    return {'message': 'Error was not caught.'}


#Login a user
@app.route('/login', methods=['GET'])
def login():
    username_email = request.json['username_email']
    username = profile.query.filter_by(username = username_email).first()
    email = profile.query.filter_by(email = username_email).first()

    if email:
        if bcrypt.check_password_hash(email.password, request.json['password']):
            token = profile.encode_auth_token(email.profile_id)
            return jsonify({'token' : token})
           
    if username:
        if bcrypt.check_password_hash(username.password, request.json['password']):
            token = profile.encode_auth_token(username.profile_id)
            return jsonify({'token' : token})
            
    
    return {'message': 'username/email and password combination is incorrect'}
    


#Search for a user
@app.route('/user', methods=['GET'])
@token_required
def user():
    result = profile.query.all()    

    return profiles_schema.jsonify(result)


#search all coffee drinks
@app.route('/allDrinks', methods=['GET'])
@token_required
def all_users(profile_id):

    all_drinks = drink.query.all()

    result = profiles_schema.dump(all_drinks)

    return jsonify(result)

#search one coffee drink
@app.route('/oneDrink', methods=['POST'])
@token_required
def one_drink(drink_id):
    
    drink_id = request.json['drink_id']

    one_drink = drink.query.get(drink_id)

    return drink_schema.jsonify(one_drink)

#create a coffee drink  (/create_drink/<name>/<is_hot>/<bean_type>/<roast_type>/<drink_type>/<creamer_type>/<sugar_type/<milk_type>/<drink_location>/<profile_id>)
@app.route('/create_drink', methods=['POST'])
@token_required
def add_drink():
    
    name = request.json['name']
    is_hot = request.json['is_hot']
    bean_type = request.json['bean_type']
    roast_type = request.json['roast_type']
    drink_type = request.json['drink_type']
    creamer_type = request.json['creamer_type']
    sugar_type = request.json['sugar_type']
    milk_type = request.json['milk_type']
    drink_location = request.json['drink_location']
    profile_id = request.json['profile_id']

    if name and is_hot and bean_type and roast_type and drink_type and creamer_type and sugar_type and milk_type and drink_location and profile_id:
        one_drink = drink(name, is_hot, bean_type, roast_type, drink_type, creamer_type, sugar_type, milk_type, drink_location, profile_id)
        db.session.add(one_drink)
        db.session.commit()
        return drink_schema.jsonify(one_drink)

@app.route('/oneFriend/<friend_id>', methods=['GET', 'PUT'])
@token_required
def one_Friend(friend_id):
    
    friend_id = request.json['friend_id']

    one_friend = drink.query.get(friend_id)

    return drink_schema.jsonify(one_friend)

@app.route('/allFriends', methods=['GET'])
@token_required
def all_friends(friend_id):
    
    friend_id = request.json['friend_id']

    one_friend = drink.query.get(friend_id)

    return drink_schema.jsonify(one_friend)

#Run Server
if __name__ == '__main__':
    app.run(debug=True)