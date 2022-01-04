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
from subFiles.model import db, profile, friend, drink, group_order, member
from subFiles.marsh import ma, ProfileSchema, DrinkSchema, FriendSchema, GroupOrderSchema, MembersSchema
from subFiles.marsh import profile_schema, drink_schema, friend_schema, groupOrder_schema, member_schema
from subFiles.marsh import profiles_schema, drinks_schema, friends_schema, groupOrders_schema, members_schema



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
            print(token)
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
    description = request.json['description']

    existing_email = profile.query.filter_by(email=email).first()
    existing_username = profile.query.filter_by(username=username).first()  
    
    if not existing_email and not existing_username:
        new_user = profile(username,first_name, last_name, email, hashed_password, description)     
        db.session.add(new_user)
        db.session.commit()
        return {'message': 'User has been created!.'}, 200
    
    if existing_email: 
        return {'message': 'Email is already in use.'}, 400
    
    if existing_username: 
        return {'message': 'Username is already in use.'}, 400
    
    return {'message': 'Error was not caught.'}, 400


#Login a user
@app.route('/login', methods=['POST'])
def login():
    username_email = request.json['username_email']
    print(username_email)
    username = profile.query.filter_by(username = username_email).first()
    email = profile.query.filter_by(email = username_email).first()

    if email:
        if bcrypt.check_password_hash(email.password, request.json['password']):
            token = profile.encode_auth_token(email.profile_id)
            return profile_schema.jsonify(email)
           
    if username:
        if bcrypt.check_password_hash(username.password, request.json['password']):
            token = profile.encode_auth_token(username.profile_id)
            return profile_schema.jsonify(username)
            
    
    return {'message': 'username/email and password combination is incorrect'}, 400
    
'''
All the routes a user's Profile



'''


#Search for all profile
@app.route('/profile/all', methods=['GET'])
#@token_required
def profile_all():
    if request.method == 'GET':
        all_profiles = profile.query.all()

        result = profiles_schema.dump(all_profiles)
        return profiles_schema.jsonify(result)

    return {'message': 'Failed HTTP request.'}, 400

#Search for a profile
@app.route('/profile/<int:profile_id>', methods=['GET'])
#@token_required
def profile_one(profile_id):
    
    result = profile.query.filter_by(profile_id = profile_id).first()
    
    if result:
    
        return profile_schema.jsonify(result), 200
    
    return {'message': 'Nothing in result'}, 400


@app.route('/profile/update', methods=['PUT'])
@token_required
def profile_update():
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
    
    
# deletes a current friend
@app.route('/profile/delete/<int:profile_id>', methods=['DELETE'])
@token_required
def profile_delete(profile_id):
    
    if profile_id:
        
        profile.query.filter_by(profile_id = profile_id).delete()

        db.session.commit()
        
        if friend.query.filter_by(profile_id = profile_id).first():
            
            return {'message': 'The friend was deleted .'}, 200
        
        return {'message': 'The friend was deleted .'}, 200

    return {'message': 'No Profile found.'}, 400
    
'''
All the routes for user Drinks



'''

# returns all drinks for one user
'''
Param: None
'''
@app.route('/drink/all/<int:profile_id>', methods=['POST'])
# @token_required
def drinks_all(profile_id):
    
    print(profile_id)
    all_drinks = drink.query.filter_by(profile_id = profile_id)
    result = drinks_schema.dump(all_drinks)

    
    return drinks_schema.jsonify(result)

# Searches for one drink
'''
Param: drink_id 
'''
@app.route('/drink/one/<int:drink_id>', methods=['POST'])
#@token_required
def one_drink(drink_id):
    
    # drink_id = request.json['drink_id']

    one_drink = drink.query.filter_by(drink_id = drink_id).first()
    
    if one_drink:
        return drink_schema.jsonify(one_drink)
    return {'message':'There are no drinks with that id.'}, 404

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
#token_required
def add_drink():
        
    #for one drink object
    name = request.json['name']
    temperature = request.json['temperature']
    bean_type = request.json['bean_type']
    roast_type = request.json['roast_type']
    drink_type = request.json['drink_type']
    creamer_type = request.json['creamer_type']
    sugar_type = request.json['sugar_type']
    milk_type = request.json['milk_type']
    flavor = request.json['flavor']
    drink_location = request.json['drink_location']
    is_favorite = request.json['is_favorite']
    profile_id = request.json['profile_id']
    
    #add_ons for this drink object
    room_for_creamer = request.json['room_for_creamer']
    room_for_milk = request.json['room_for_milk']
    number_of_sugar_bags = request.json['number_of_sugar_bags']
    isSteamed = request.json['isSteamed']
    extra_comments = request.json['extra_comments']
                
    one_drink = drink(name,
                        temperature,
                        bean_type,
                        roast_type,
                        drink_type,
                        creamer_type,
                        sugar_type,
                        milk_type,
                        flavor,
                        drink_location,
                        is_favorite,
                        profile_id,
                        room_for_creamer,
                        room_for_milk,
                        number_of_sugar_bags,
                        isSteamed,
                        extra_comments)
    if one_drink:
        db.session.add(one_drink)
        db.session.commit()
        return {'message': 'Drink has been created!'}, 200
            
        
    return {'message': 'The drink was not created in the database'}, 403

# update an existing drink
'''
Drink Model

Param: name 
Param: temperature 
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
#@token_required
def update_drink():                     
    #for one drink object
    name = request.json['name']
    temperature = request.json['temperature']
    bean_type = request.json['bean_type']
    roast_type = request.json['roast_type']
    drink_type = request.json['drink_type']
    creamer_type = request.json['creamer_type']
    sugar_type = request.json['sugar_type']
    milk_type = request.json['milk_type']
    flavor = request.json['flavor']
    drink_location = request.json['drink_location']
    is_favorite = request.json['is_favorite']
    drink_id = request.json['drink_id']
    
    #add_ons for this drink object
    room_for_creamer = request.json['room_for_creamer']
    room_for_milk = request.json['room_for_milk']
    number_of_sugar_bags = request.json['number_of_sugar_bags']
    isSteamed = request.json['isSteamed']
    extra_comments = request.json['extra_comments']     
            
    
    if drink_id and name and temperature and bean_type and roast_type and drink_type and creamer_type and sugar_type and milk_type and drink_location:
        
        if number_of_sugar_bags and extra_comments:
            
            current_drink = drink.query.filter_by(drink_id = drink_id).first()
            if current_drink:
                
                updated_drink = drink.update(current_drink,
                                            name,
                                            temperature,
                                            bean_type, 
                                            roast_type, 
                                            drink_type, 
                                            creamer_type, 
                                            sugar_type, 
                                            milk_type, 
                                            flavor,
                                            drink_location,
                                            is_favorite, 
                                            room_for_creamer, 
                                            number_of_sugar_bags,
                                            room_for_milk, 
                                            isSteamed, 
                                            extra_comments
                                            )
            else:
                return {'message': 'Failed to find drink and add_on in the database.'}, 404
            
            if updated_drink:
                return drink_schema.jsonify(updated_drink), 200
    
    return {'message': 'Danger database failed to update'}, 408
    
# deletes a current friend
@app.route('/drink/delete/<int:drink_id>', methods=['DELETE'])
#@token_required
def drink_delete(drink_id):        

    
    if drink_id:
        
        drink.query.filter_by(drink_id = drink_id).delete()


        db.session.commit()
        
        if drink.query.filter_by(drink_id = drink_id):
                
            return {'message': 'The friend was not deleted .'}, 200
        
        return {'message': 'The friend was deleted .'}, 200

    return {'message': 'No Profile found.'}, 400
    

'''
All the routes for user Friends



'''
 # Adds a friendship 
'''
Param: profile_id 
Param: friend_id
'''    
@app.route('/friend/add', methods=['POST'])
#@token_required
def friend_add():
    profile_id = request.json['profile_id']
    friend_id = request.json['friend_id']
    
    if friend_id and profile_id:
        friendship_a = friend(profile_id, friend_id)
        friendship_b = friend(friend_id, profile_id)
        data = {friendship_a, friendship_b}
        db.session.add_all(data)
        db.session.commit()
        return friend_schema.jsonify(friendship_a)

    return {'message': 'No Profile from that friend id.'}, 400 

@app.route('/friends/profile/all', methods=['GET'])
#@token_required
def friend_profile_all():
    if request.method == 'GET':
        all_profiles = profile.query.all()

        result = profiles_schema.dump(all_profiles)
        return profiles_schema.jsonify(result)

    return {'message': 'Failed HTTP request.'}, 400


# Returns the friends profile details
'''
Param: profile_id 
Param: friend_id
'''    
@app.route('/friend/profile', methods=['GET'])
#@token_required
def friend_profile():
    profile_id = request.json['profile_id']
    friend_id = request.json['friend_id']
    if friend_id and profile_id:
        friendship = friend.query.filter_by(user_a = friend_id, user_b = profile_id).first()
        return friend_schema.jsonify(friendship)

    return {'message': 'No Profile from that friend id.'}, 400       
       
# returns an array of friends filtered by profile_id
'''
Param: profile_id
''' 
@app.route('/friend/list/<int:profile_id>', methods=['GET'])
#@token_required
def friend_list(profile_id):
    
    if profile_id:
        
        if friend.query.filter_by(user_a = profile_id).first():
            friend_list = friend.query.filter_by(user_a = profile_id)
            if friend_list:
                result = friends_schema.dump(friend_list)
                return friends_schema.jsonify(result)
            return {'message': 'There are no friends'}, 200

    return {'message': 'No Profile from that friend id.'}, 400
    


# deletes an existing friend
'''
Param: profile_id 
Param: friend_id
''' 
@app.route('/friend/delete', methods=['DELETE'])
#@token_required
def friend_delete():
    profile_id = request.json['profile_id']  
    friend_id = request.json['friend_id']
    if friend_id and profile_id:
        friend.query.filter_by(user_a = friend_id, user_b = profile_id).delete()
        friend.query.filter_by(user_b = friend_id, user_a = profile_id).delete()

        db.session.commit()
        
        if friend.query.filter_by(user_a = friend_id, user_b = profile_id):
            
            return {'message': 'The friend was not deleted .'}, 200
        
        return {'message': 'The friend was deleted .'}, 200

    return {'message': 'No Profile from that friend id.'}, 400

'''
All the routes for user group_orders



'''

# Creates a group order
'''

Param: name
Param: order_location
Param: order_time
Param: is_admin
Param: is_active
''' 
@app.route('/grouporder/create', methods=['POST'])
#@token_required
def group_order_create():
    order_location = request.json['order_location']
    order_time = request.json['order_time']
    admin = request.json['admin']
    is_active = request.json['is_active']
    name = request.json['name']
    date = request.json['date']
    address = request.json['address']
    
    print(order_location)
    print(order_time)
    print(admin)
    print(is_active)
    print(name)
    print(date)
    print(address)

    
    if order_location and order_time and admin and name and date and address:
        
        new_group_order = group_order(name, order_location, order_time, admin, is_active, date, address)
        
        if new_group_order:
            print(groupOrder_schema.jsonify(new_group_order))
            
            db.session.add(new_group_order)
            db.session.commit()
            
            add_member = member(new_group_order.group_id, new_group_order.admin)
            print(member_schema.jsonify(add_member))

            db.session.add(add_member)
            db.session.commit()
            
            
            return member_schema.jsonify(add_member)
        
        return {'message': 'Failed to create group order.'}, 403
    
    return {'message': 'Failed to read request contents'}, 400



# This will update an existing order
'''
Param: name
Param: group_id
Param: order_location
Param: order_time
Param: is_admin
Param: is_active
''' 
@app.route('/grouporder/<int:group_id>', methods=['GET'])
#@token_required
def group_order_update(group_id):
    
    if group_id:        
        print(group_id)
        has_orders = group_order.query.filter_by(group_id = group_id).first()

        if has_orders:
            pprint(has_orders)

            return groupOrder_schema.jsonify(has_orders)
        
        return {'message': 'Failed to find current group order.'}, 403
    
    return {'message': 'Failed to read request contents'}, 400
    

# Deletes an existing group order
'''
Param: group_id
'''
@app.route('/grouporder/delete', methods=['DELETE'])
#@token_required
def group_order_delete():
    if request.method == 'DELETE':
        
        group_id = request.json['group_id']
        if group_id:
            group_order.query.filter_by(group_id = group_id).delete()
            
            db.session.commit()
            
            if group_order.query.filter_by(group_id = group_id):
                
                return {'message': 'The group order was not deleted .'}, 200
            
            return {'message': 'The group order was deleted .'}, 200

        return {'message': 'No group order from that group id.'}, 400
    
    return {'message': 'HTTP request was invalid.'}, 400

'''
All for the routes Members of a Group Order



'''

'''
add memebers to a group order
Param: username
Param: group_id
Param: coffee
''' 
@app.route('/member/add', methods=['POST'])
#@token_required
def members_create():
    username = request.json['username']
    group_id = request.json['group_id']
    coffee = request.json['coffee']

    
    if username and group_id and coffee:
        
        new_members = member(group_id, username, coffee)
        if new_members:
            db.session.add(new_members)
            db.session.commit()
            
            return member_schema.jsonify(new_members)
        return {'message': 'Failed to add group order.'}, 403
    
    return {'message': 'Failed to read request contents'}, 400

@app.route('/member/delete', methods=['DELETE'])
#@token_required
def members_update():
    member_id = request.json['id']
    
    if member_id:
        
        new_members = member(member_id)
        if new_members:
            db.session.add(new_members)
            db.session.commit()
            
            return member_schema.jsonify(new_members)
        return {'message': 'Failed to add group order.'}, 403
    
    return {'message': 'Failed to read request contents'}, 400

@app.route('/member/all/<string:username>', methods=['GET'])
#@token_required
def members_orders(username):
    print(username)
    if username:
        #drink.query.filter_by(profile_id = profile_id)
        check_group_orders = member.query.filter_by(username = username)
        
        if check_group_orders:
            result = members_schema.dump(check_group_orders)
            
            return members_schema.jsonify(result), 200
        return {'message': 'Failed to add group order.'}, 403
    
    return {'message': 'Failed to read request contents'}, 400

@app.route('/member/all', methods=['GET'])
#@token_required
def members_all():

    #drink.query.filter_by(profile_id = profile_id)
    check_group_orders = member.query.all()
    
    if check_group_orders:
        result = members_schema.dump(check_group_orders)
        
        return members_schema.jsonify(result), 200
    return {'message': 'Failed to add group order.'}, 403
    
#Run Server
if __name__ == '__main__':
    app.run(debug=True)