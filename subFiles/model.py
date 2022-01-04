from sqlalchemy import Column, ForeignKey, Integer, String, Table, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import expression
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.sql.sqltypes import Boolean
import jwt
from pprint import pprint



from subFiles.config import app

db = SQLAlchemy(app)

# Base = declarative_base()
# metadata = Base.metadata

# Coffee Break Class/Models

class profile(db.Model):
    __tablename__ = 'profile'

    profile_id = db.Column('profile_id', db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column('first_name', db.String(50), nullable=False)
    last_name = db.Column('last_name', db.String(50), nullable=False)
    username = db.Column('username', db.String(50), nullable=False, unique=True)
    email = db.Column('email', db.String(50), nullable=False, unique=True)
    password = db.Column('password', db.String(100), nullable=False)
    description = db.Column('description', db.String(200), nullable=True)
    created_at = db.Column('created_at',db.DateTime, default=datetime.utcnow)

    # relationship with coffee drinks
    drinks = db.relationship('drink', backref='owner', lazy=True, foreign_keys='[drink.profile_id]')

    #relationship with friend users
    friend_a = db.relationship('friend', backref='a', lazy=True, foreign_keys='[friend.user_a]')
    friend_b = db.relationship('friend', backref='b', lazy=True, foreign_keys='[friend.user_b]')
    
    # relationship with group orders
    group_order = db.relationship('group_order', cascade="all,delete" , backref='owner', lazy=True, foreign_keys='[group_order.admin]')
    
    #relationship with members for a group order
    members = db.relationship('member', cascade="all,delete", backref='members', lazy=True, foreign_keys='[member.username]')

    def __init__(self, username, first_name, last_name, email, password, description):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.description = description
        
    def encode_auth_token(profile_id):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'id': profile_id,
                'exp': datetime.utcnow() + timedelta(days=7),
                'iat': datetime.utcnow(),  
            }
            token = jwt.encode(
                payload,
                app.config['SECRET_KEY'],
                algorithm='HS256'
            )
            return token
        except Exception as e:
            return e


class friend(db.Model):
    __tablename__ = 'friend'

    friend_id = db.Column('friend_id', db.Integer, primary_key=True, autoincrement=True)

    # Foreign key linking friend user to profile
    user_a = db.Column('user_a', db.Integer, db.ForeignKey('profile.profile_id'), nullable=False)
    user_b = db.Column('user_b', db.Integer, db.ForeignKey('profile.profile_id'), nullable=False)

    def __init__(self, user_a, user_b):
        self.user_a = user_a
        self.user_b = user_b        
    
    def befriend(user_b, user_a):
        friend(user_b, user_a)
        

class drink(db.Model):
    __tablename__ = 'drink'
    
    #Drink
    drink_id = db.Column('drink_id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(50), nullable=False)
    temperature = db.Column('temperature', db.String(50), nullable=False)
    bean_type = db.Column('bean_type', db.String(50), nullable=False)
    roast_type = db.Column('roast_type', db.String(50), nullable=False)
    drink_type = db.Column('drink_type', db.String(50), nullable=False)
    creamer_type = db.Column('creamer_type', db.String(50), nullable=False)
    sugar_type = db.Column('sugar_type', db.String(50), nullable=False)
    milk_type = db.Column('milk_type', db.String(50), nullable=False)
    flavor = db.Column('flavor', db.String(50), nullable=False)
    drink_location = db.Column('drink_location', db.String(50), nullable=False)
    is_favorite = db.Column('is_favorite', db.Boolean, nullable=False)

    #Add ons
    room_for_milk = db.Column('room_for_milk', db.Boolean, nullable=False)
    room_for_creamer = db.Column('room_for_creamer', db.Boolean, nullable=False)
    number_of_sugar_bags = db.Column('number_of_sugar_bags', db.Integer, nullable=False)
    isSteamed = db.Column('isSteamed', db.Boolean, nullable=False)
    extra_comments = db.Column('extra_comments', db.String(100), nullable=True)
    created_at = db.Column('created_at',db.DateTime, default=datetime.utcnow)

    # Foreign key linking coffee drink to profile of the creator
    profile_id = db.Column('profile_id', db.Integer, db.ForeignKey('profile.profile_id'), nullable=False)
    
    # relationship with members of a group order
    coffee = db.relationship('member', backref ='order_drink', lazy=True)

    


    def __init__(self,
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
                profile_id, 
                room_for_creamer,
                room_for_milk, 
                number_of_sugar_bags, 
                isSteamed, 
                extra_comments):
        #Drink
        self.name = name
        self.temperature = temperature
        self.bean_type = bean_type
        self.roast_type = roast_type
        self.drink_type = drink_type
        self.creamer_type = creamer_type
        self.sugar_type = sugar_type
        self.milk_type = milk_type
        self.flavor = flavor
        self.drink_location = drink_location
        self.is_favorite = is_favorite
        self.profile_id = profile_id
        #Add Ons
        self.room_for_creamer = room_for_creamer
        self.room_for_milk = room_for_milk
        self.number_of_sugar_bags = number_of_sugar_bags
        self.isSteamed = isSteamed
        self.extra_comments = extra_comments


    '''
    update fields of an drink object in the database
    param: name
    param: is_hot
    param: bean_type
    param: level_of_roast
    param: drink_type
    param: creamer_type
    param: sugar_type
    param: milk_type
    param: drink_location
    param: is_favorite
    
    update fields of an add on object in the database
    param: room_for_creamer
    param: number_of_sugar_bags
    param: milk_texture
    param: extra_comments
    '''

    def update(
            self,
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
            ):
                
        if name is not None:
            self.name = name
            
        if temperature is not None:
            self.temp = temperature
            
        if bean_type is not None:
            self.bean_type = bean_type
            
        if roast_type is not None:
            self.roast_type = roast_type
            
        if drink_type is not None:
            self.drink_type = drink_type
            
        if creamer_type is not None:
            self.creamer_type = creamer_type
            
        if sugar_type is not None:
            self.sugar_type = sugar_type
            
        if milk_type is not None:
            self.milk_type = milk_type
            
        if flavor is not None:
            self.flavor = flavor
            
        if is_favorite is not None:
            self.is_favorite = is_favorite
            
        if creamer_type is not None:
            self.drink_location = drink_location
            
        if number_of_sugar_bags is not None:
            self.number_of_sugar_bags = number_of_sugar_bags
            
        if room_for_creamer is not None:
            self.room_for_creamer = room_for_creamer
            
        if room_for_milk is not None:
            self.room_for_milk = room_for_milk
            
        if isSteamed is not None:
            self.isSteamed = isSteamed
            
        if extra_comments is not None:
            self.extra_comments = extra_comments
            
        db.session.commit()
        return self
        
        # maybe add an update to the created_at     

class group_order(db.Model):
    __tablename__ = 'group_order'

    group_id = db.Column('group_id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(100), nullable=False)
    order_location = db.Column('order_location', db.String(100), nullable=False)
    order_time = db.Column('order_time', db.String(50), nullable=False)
    date = db.Column('date', db.String(75), nullable=False)
    address = db.Column('address', db.String(75), nullable=False)
    is_active = db.Column('is_active', db.Boolean, nullable = False)
    created_at = db.Column('created_at',db.DateTime, default=datetime.utcnow)
    
    # Foreign key linking profile to the admin of a group order
    admin = db.Column('admin', db.String, db.ForeignKey('profile.username'), nullable=False)

    # relationship for the members of the group order to store in table
    member = db.relationship('member', cascade="all,delete", backref ='order_member', lazy=True)


    def __init__(self, name, order_location, order_time, admin, is_active, date, address):
        self.name = name
        self.admin = admin
        self.order_location = order_location
        self.order_time = order_time  
        self.is_active = is_active 
        self.date = date
        self.address = address
    '''
    update fields of an add on object in the database
    param: name
    param: admin
    param: order_location
    param: order_time
    param: is_active
    '''
    def update(self, name, admin, order_location, order_time, is_active, date, address ):
        if name is not None:
            self.name = name
        if admin is not None:
            self.admin = admin
        if order_location is not None:
            self.order_location = order_location
        if order_time is not None:
            self.order_time = order_time
        if is_active is not None:
            self.is_active = is_active
        if date is not None:
            self.date = date
        if address is not None:
            self.address = address
            
        db.session.commit()
        return self
        

class member(db.Model):
    __tablename__ = 'member'

    member_id = db.Column('member_id', db.Integer, primary_key = True, autoincrement= True)
    
    # Foreign key linking group order to the members of that specific group order
    group_id = db.Column('group_id', db.Integer, db.ForeignKey('group_order.group_id'), nullable = False)

    # Foreign key linking profile to the member of a group order
    username = db.Column('username', db.String, db.ForeignKey('profile.username'), nullable=False)
    
    # Foreign key linking drink to the member of a group order
    coffee = db.Column('coffee', db.String, db.ForeignKey('drink.name'), nullable=True)

    def __init__(self, group_id, username):
        self.group_id = group_id
        self.username = username
        
    
