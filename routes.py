from hashlib import new
from pprint import pprint
import re
from weakref import WeakKeyDictionary
from flask import request, jsonify
from marshmallow.fields import Email
from sqlalchemy.orm import query, session
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
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except:
            return jsonify({'message' : 'Token is invalid'}), 403
        
        return func(*args, **kwargs)
    return decorated

    
'''
The routes for both signing up and login



'''

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
        return {'message': 'Email is already in use.'}, 400
    
    if existing_username: 
        return {'message': 'Username is already in use.'}, 400
    
    return {'message': 'Error was not caught.'}, 400


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
    
'''
All the routes a user's Profile



'''


#Search for all profile
@app.route('/profile/all', methods=['GET'])
@token_required
def profile_all():
    if request.method == 'GET':
        all_profiles = profile.query.all()
        pprint(all_profiles)

        result = profiles_schema.dump(all_profiles)
        pprint(result)
        return profiles_schema.jsonify(result)

    return {'message': 'Failed HTTP request.'}, 400

#Search for a profile
@app.route('/profile', methods=['GET'])
@token_required
def profile_one():
    if request.method == 'GET':
        result = profile.query.filter_by(profile_id = request.json['profile_id']).first()
        
        if result:
        
            return profile_schema.jsonify(result), 200
        return {'message': 'Nothing in result'}, 400

    return {'message': 'Failed HTTP request.'}, 400


@app.route('/profile/update', methods=['PUT'])
@token_required
def profile_update():
    if request.method == 'PUT':
        
        current_profile = profile.query.filter_by(profile_id = request.json['profile_id']).first()
        
        if current_profile:
            current_profile.username = request.json['username']
            current_profile.password = bcrypt.generate_password_hash(request.json['password']).decode('utf-8')
            current_profile.first_name = request.json['first_name']
            current_profile.last_name = request.json['last_name']
            current_profile.email = request.json['email']
            db.session.commit()
            return profile_schema.jsonify(current_profile), 200
            
        return {'message': 'Failed to update profile'}, 400
    
    return {'message': 'HTTP reuest was invalid.'}, 400

# deletes a current friend
@app.route('/profile/delete', methods=['DELETE'])
@token_required
def profile_delete():
    if request.method == 'DELETE':
        
        profile_id = request.json['profile_id']
        
        if profile_id:
            
            profile.query.filter_by(profile_id = profile_id).delete()

            db.session.commit()
            
            if friend.query.filter_by(profile_id = profile_id).first():
                
                return {'message': 'The friend was not deleted .'}, 200
            
            return {'message': 'The friend was deleted .'}, 200

        return {'message': 'No Profile found.'}, 400
    
    return {'message': 'HTTP reuest was invalid.'}, 400

'''
All the routes for user Drinks



'''

# returns all drinks for one user
'''
Param: None
'''
@app.route('/drink/all', methods=['GET'])
@token_required
def drinks_all():
    if request.method == 'GET':
        all_drinks = drink.query.all()

        result = drinks_schema.dump(all_drinks)
        
        return drinks_schema.jsonify(result)

    return {'message': 'Failed HTTP request.'}, 400

# Searches for one drink
'''
Param: drink_id 
'''
@app.route('/drink/one', methods=['GET'])
@token_required
def one_drink(drink_id):
    
    drink_id = request.json['drink_id']

    one_drink = drink.query.filter_by(drink_id)

    return drink_schema.jsonify(one_drink)

# Creates one drink 
'''
Drink Model

Param: name 
Param: is_hot 
Param: drink_id 
Param: bean_type 
Param: roast_type 
Param: drink_type 
Param: creamer_type 
Param: sugar_type
Param: milk_type 
Param: drink_location 
Param: is_favorite 
Param: profile_id 

Add_On Model

Param: creamer_level 
Param: number_of_sugar_bags 
Param: milk_texture 
Param: extra_comments 
Param: drink_id 
'''
@app.route('/drink/create', methods=['POST'])
@token_required
def add_drink():
        
    if request.method == 'POST':
        #for one drink object
        name = request.json['name']
        is_hot = request.json['is_hot']
        bean_type = request.json['bean_type']
        roast_type = request.json['roast_type']
        drink_type = request.json['drink_type']
        creamer_type = request.json['creamer_type']
        sugar_type = request.json['sugar_type']
        milk_type = request.json['milk_type']
        drink_location = request.json['drink_location']
        is_favorite = request.json['is_favorite']
        profile_id = request.json['profile_id']
        
        #add_ons for this drink object
        creamer_level = request.json['creamer_level']
        number_of_sugar_bags = request.json['number_of_sugar_bags']
        milk_texture = request.json['milk_texture']
        milk_level = request.json['milk_level']
        extra_comments = request.json['extra_comments']
        drink_id = request.json['drink_id']
        
        
        if name and is_hot and bean_type and roast_type and drink_type and creamer_type and sugar_type and milk_type and drink_location and is_favorite and profile_id:
            
            if creamer_level and number_of_sugar_bags and milk_texture and milk_level and extra_comments and drink_id:
            
                if request.method == 'POST':
                    
                    one_drink = drink(name, is_hot, bean_type, roast_type, drink_type, creamer_type, sugar_type, milk_type, drink_location, profile_id)
                    
                    if one_drink:
                        db.session.add(one_drink)
                        db.session.commit()
                    
                    drink_add_ons = add_on(creamer_level, number_of_sugar_bags, milk_texture, milk_level, extra_comments, drink_id)
                    
                    if drink_add_ons:
                        db.session.add(drink_add_ons)
                        db.session.commit()
                        return {drink_schema.jsonify(one_drink),addOn_schema.jsonify(drink_add_ons)}
                    
                    
                    return {'message': 'Danger database failed to update'}, 403
            
            return {'message': 'one or more of the add on object fields is incorrect'}, 403
    
    return {'message': 'one or more of the drink object fields is incorrect'}, 403    

# update an existing drink
'''
Drink Model

Param: name 
Param: is_hot 
Param: drink_id 
Param: bean_type 
Param: roast_type 
Param: drink_type 
Param: creamer_type 
Param: sugar_type
Param: milk_type 
Param: drink_location 
Param: is_favorite 
Param: profile_id 

Add_On Model

Param: creamer_level 
Param: number_of_sugar_bags 
Param: milk_texture 
Param: extra_comments 
Param: drink_id 
'''
@app.route('/drink/update', methods=['PUT'])
@token_required
def update_drink():    
    if request.method == 'PUT':
                 
        #for one drink object
        name = request.json['name']
        temperature = request.json['temperature']
        bean_type = request.json['bean_type']
        roast_type = request.json['roast_type']
        drink_type = request.json['drink_type']
        creamer_type = request.json['creamer_type']
        sugar_type = request.json['sugar_type']
        milk_type = request.json['milk_type']
        drink_location = request.json['drink_location']
        is_favorite = request.json['is_favorite']
        profile_id = request.json['profile_id']
        
        #add_ons for this drink object
        creamer_level = request.json['creamer_level']
        number_of_sugar_bags = request.json['number_of_sugar_bags']
        milk_texture = request.json['milk_texture']
        extra_comments = request.json['extra_comments']
        drink_id = request.json['drink_id']       
                

        
        if name and temperature and bean_type and roast_type and drink_type and creamer_type and sugar_type and milk_type and drink_location and is_favorite and profile_id:
            
            if creamer_level and number_of_sugar_bags and milk_texture and extra_comments and drink_id:
                
                current_drink = drink.query.filter_by(drink_id = drink_id)
                current_add_on = add_on.query.filter_by(drink_id = drink_id)
                
                if current_drink and current_add_on:
                    
                    updated_drink = drink.update(current_drink, name, temperature, bean_type, roast_type, drink_type, creamer_type, sugar_type, milk_type, drink_location, profile_id)
                    updated_add_ons = add_on.update(current_add_on, creamer_level, number_of_sugar_bags, milk_texture, extra_comments, drink_id)
                    
                else:
                    
                    return {'message': 'Failed to find drink and add_on in the database.'}, 40

                if updated_drink and updated_add_ons:
                    
                    return {drink_schema.jsonify(updated_drink)}
        
        return {'message': 'Danger database failed to update'}, 403
    
    return {'message': 'HTTP reuest was invalid.'}, 400


'''
All the routes for user Friends



'''
 
# Returns the friends profile details
'''
Param: friend_id
'''    
@app.route('/friend/profile', methods=['GET'])
@token_required
def friend_profile():
    if request.method == 'GET':
        friend_id = request.json['friend_id']
        if friend_id:
            friend_profile = profile.query.filter_by(friend_id)
            return profile_schema.jsonify(friend_profile)

        return {'message': 'No Profile from that friend id.'}, 400
    
    return {'message': 'HTTP reuest was invalid.'}, 400
       
       
# returns an array of friends filtered by profile_id
'''
Param: profile_id
''' 
@app.route('/friend/list', methods=['GET'])
@token_required
def friend_list():
    if request.method == 'GET':
        profile_id = request.json['profile_id']
        if profile_id:
            friend_list = friend.query.filter_by(profile_id)
            result = friends_schema.dump(friend_list)
            return friends_schema.jsonify(result)

        return {'message': 'No Profile from that friend id.'}, 400
    
    return {'message': 'HTTP reuest was invalid.'}, 400


# deletes an existing friend
'''
Param: friend_id
''' 
@app.route('/friend/delete', methods=['DELETE'])
@token_required
def friend_delete():
    if request.method == 'DELETE':
        
        friend_id = request.json['friend_id']
        if friend_id:
            friend.query.filter_by(friend_id = friend_id).delete()
            
            db.session.commit()
            
            if friend.query.filter_by(friend_id = friend_id):
                
                return {'message': 'The friend was not deleted .'}, 200
            
            return {'message': 'The friend was deleted .'}, 200

        return {'message': 'No Profile from that friend id.'}, 400
    
    return {'message': 'HTTP reuest was invalid.'}, 400


'''
All the routes for user group_orders



'''

# Creates a group order
'''
Param: order_location
Param: order_time
Param: is_admin
Param: is_active
''' 
@app.route('/grouporder/create', methods=['POST'])
@token_required
def group_order_create():
    if request.method == 'POST':
        order_location = request.json['order_location']
        order_time = request.json['order_time']
        is_admin = request.json['is_admin']
        is_active = request.json['is_active']
        
        if order_location and order_time and is_admin and is_active:
            
            new_group_order = group_order(order_location, order_time, is_admin, is_active)
            if new_group_order:
                db.session.add(new_group_order)
                db.session.commit()
                
                return groupOrder_schema.jsonify(new_group_order)
            return {'message': 'Failed to create group order.'}, 403
        
        return {'message': 'Failed to read request contents'}, 400
    
    return {'message': 'HTTP request was invalid.'}, 400


# This will update an existing order
'''
Param: group_id
Param: order_location
Param: order_time
Param: is_admin
Param: is_active
''' 
@app.route('/grouporder/update', methods=['PUT'])
@token_required
def group_order_update():
    
    if request.method == 'PUT':
        group_id = request.json['group_id']
        order_location = request.json['order_location']
        order_time = request.json['order_time']
        is_active = request.json['is_active']
        is_admin = request.json['is_admin']
        
        if group_id and order_location and order_time and is_active and is_admin:
            
            current_order = drink.query.filter_by(group_id = group_id)
     
            if current_order:
                
                updated_group_order = group_order.update(current_order, is_admin, order_location, order_time, is_active)
                if updated_group_order:
                    db.session.commit()
                
                return groupOrder_schema.jsonify(updated_group_order)
            
            return {'message': 'Failed to find current group order.'}, 403
        
        return {'message': 'Failed to read request contents'}, 400
    
    return {'message': 'HTTP request was invalid.'}, 400


# Deletes an existing group order
'''
Param: group_id
'''
@app.route('/grouporder/delete', methods=['DELETE'])
@token_required
def group_order_delete():
    if request.method == 'DELETE':
        
        group_id = request.json['group_id']
        if group_id:
            group_order.query.filter_by(group_id = group_id).delete()
            
            db.session.commit()
            
            if friend.query.filter_by(group_id = group_id):
                
                return {'message': 'The group order was not deleted .'}, 200
            
            return {'message': 'The group order was deleted .'}, 200

        return {'message': 'No group order from that group id.'}, 400
    
    return {'message': 'HTTP request was invalid.'}, 400


#Run Server
if __name__ == '__main__':
    app.run(debug=True)