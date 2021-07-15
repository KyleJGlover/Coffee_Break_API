from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import expression
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.sql.sqltypes import Boolean
import jwt

from subFiles.config import app

db = SQLAlchemy(app)

Base = declarative_base()
metadata = Base.metadata

# Coffee Break Class/Models

class profile(db.Model, UserMixin):
    __tablename__ = 'profile'

    profile_id = db.Column('profile_id', db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column('first_name', db.String(50), nullable=False)
    last_name = db.Column('last_name', db.String(50), nullable=False)
    username = db.Column('username', db.String(50), nullable=False, unique=True)
    email = db.Column('email', db.String(50), nullable=False, unique=True)
    password = db.Column('password', db.String(100), nullable=False)
    created_at = db.Column('created_at',db.DateTime, default=datetime.utcnow)

    # relationship with group orders
    group_order = db.relationship('group_order', backref='owner', lazy=True, foreign_keys='[group_order.is_admin]')

    # relationship with coffee drinks
    drinks = db.relationship('drink', backref='owner', lazy=True, foreign_keys='[drink.profile_id]')

    #relationship with friend users
    friends = db.relationship('friend', backref='owner', lazy=True, foreign_keys='[friend.profile_id]')

    def __init__(self, username, first_name, last_name, email, password):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        
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

    def is_authenticated(self):
        # Gives the user authentication
        return True
    


class friend(db.Model):
    __tablename__ = 'friend'

    friend_id = db.Column('friend_id', db.Integer, primary_key=True, autoincrement=True)
    friend_username = db.Column('friend_username', db.String(50), db.ForeignKey('profile.username'), nullable=False, unique=True)

    # Foreign key linking friend user to profile
    profile_id = db.Column('profile_id', db.Integer, db.ForeignKey('profile.profile_id'), nullable=False, unique=True)

    def __init__(self, friend_username, profile_id):
        self.friend_username = friend_username
        self.profile_id = profile_id

    


class drink(db.Model):
    __tablename__ = 'drink'

    drink_id = db.Column('drink_id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(50), nullable=False)
    is_hot = db.Column('is_hot', db.String(50), nullable=False)
    bean_type = db.Column('bean_type', db.String(50), nullable=False)
    roast_type = db.Column('roast_type', db.String(50), nullable=False)
    drink_type = db.Column('drink_type', db.String(50), nullable=False)
    creamer_type = db.Column('creamer_type', db.String(50), nullable=False)
    sugar_type = db.Column('sugar_type', db.String(50), nullable=False)
    milk_type = db.Column('milk_type', db.String(50), nullable=False)
    drink_location = db.Column('drink_location', db.String(50), nullable=False)
    is_favorite = db.Column('is_favorite', db.Boolean, nullable=False)

    created_at = db.Column('created_at',db.DateTime, default=datetime.utcnow)

    # Foreign key linking coffee drink to profile of the creator
    profile_id = db.Column('profile_id', db.Integer, db.ForeignKey('profile.profile_id'), nullable=False, unique=True)

    # relationship linking add ons to the coffee drink
    add_on = db.relationship('add_on', backref='add_on', lazy=True, foreign_keys='[add_on.drink_id]')

    def __init__(self, name, is_hot, bean_type, level_of_roast, drink_type, creamer_type, sugar_type, milk_type, drink_location, is_favorite, profile_id):
        self.name = name
        self.is_hot = is_hot
        self.bean_type = bean_type
        self.level_of_roast = level_of_roast
        self.drink_type = drink_type
        self.creamer_type = creamer_type
        self.sugar_type = sugar_type
        self.milk_type = milk_type
        self.drink_location = drink_location
        self.is_favorite = is_favorite
        self.profile_id = profile_id


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
    param: profile_id
    '''

    def update(
            self,
            name='',
            is_hot='',
            bean_type='', 
            level_of_roast='', 
            drink_type='', 
            creamer_type='', 
            sugar_type='', 
            milk_type='', 
            drink_location='',
            is_favorite = None, 
            profile_id = None
            ):
        if profile_id is not None:
            if profile_id > 0:
                self.profile_id = profile_id
                
        if name is not None:
            self.name = name
            
        if is_hot is not None:
            self.is_hot = is_hot
            
        if bean_type is not None:
            self.bean_type = bean_type
            
        if level_of_roast is not None:
            self.level_of_roast = level_of_roast
            
        if drink_type is not None:
            self.drink_type = drink_type
            
        if creamer_type is not None:
            self.creamer_type = creamer_type
            
        if sugar_type is not None:
            self.sugar_type = sugar_type
            
        if milk_type is not None:
            self.milk_type = milk_type
            
        if self.is_favorite:
            self.is_favorite = is_favorite
            
        if creamer_type is not None:
            self.drink_location = drink_location
        
        db.session.commit()
        return self
        
        # maybe add an update to the created_at     

class add_on(db.Model):
    __tablename__ = 'add_on'

    add_on_id = db.Column('add_on_id', db.Integer, nullable=False, primary_key=True, autoincrement=True)
    creamer_level = db.Column('creamer_level', db.String(50), nullable=False)
    number_of_sugar_bags = db.Column('number_of_sugar_bags', db.Integer, nullable=False)
    milk_texture = db.Column('milk_texture', db.String(50), nullable=False)
    milk_level = db.Column('milk_level', db.String(50), nullable=False)
    extra_comments = db.Column('extra_comments', db.String(100), nullable=True)

    # Foreign key linking add ons to coffee drink
    drink_id = db.Column('drink_id', db.Integer, db.ForeignKey('drink.drink_id'), nullable=False, unique=True)


    def __init__(self, creamer_level, number_of_sugar_bags, milk_texture, milk_level, extra_comments):
        self.creamer_level = creamer_level
        self.number_of_sugar_bags = number_of_sugar_bags
        self.milk_texture = milk_texture
        self.milk_level = milk_level
        self.extra_comments = extra_comments

    '''
    update fields of an add on object in the database
    param: add_on_id
    param: number_of_sugar_bags
    param: milk_texture
    param: milk_level
    param: extra_comments
    '''

    def update(
            self,
            add_on_id=0,
            number_of_sugar_bags='',
            milk_texture='', 
            milk_level='', 
            extra_comments='', 
            ):
        if add_on_id != 0:
            self.add_on_id = add_on_id
        if number_of_sugar_bags is not None:
            self.number_of_sugar_bags = number_of_sugar_bags
        if milk_texture is not None:
            self.milk_texture = milk_texture
        if milk_level is not None:
            self.milk_level = milk_level
        if extra_comments is not None:
            self.extra_comments = extra_comments
            
        db.session.commit()
        return self

class group_order(db.Model):
    __tablename__ = 'group_order'

    group_id = db.Column('group_id', db.Integer, primary_key=True, autoincrement=True)
    order_location = db.Column('order_location', db.String(100), nullable=False)
    order_time = db.Column('order_time', db.String(50), nullable=False)
    created_at = db.Column('created_at',db.DateTime, default=datetime.utcnow)
    
    # Foreign key linking profile to the admin of a group order
    is_admin = db.Column('is_admin', db.Integer, db.ForeignKey('profile.profile_id'), nullable=False)

    # relationship for the members of the group order to store in table
    member = db.relationship('member', backref ='order_member', lazy=True)

    def __init__(self, order_location, order_time, is_admin):
        self.is_Admin = is_admin
        self.order_location = order_location
        self.order_time = order_time   
    '''
    update fields of an add on object in the database
    param: add_on_id
    param: number_of_sugar_bags
    param: milk_texture
    param: milk_level
    param: extra_comments
    '''
    def update(self, is_Admin, order_location, order_time ):
        if is_Admin is not None:
            self.is_Admin = is_Admin
        if order_location is not None:
            self.order_location = order_location
        if order_time is not None:
            self.order_time = order_time
        
        db.session.commit()
        

class member(db.Model):
    __tablename__ = 'member'

    member_id = db.Column('member_id', db.Integer, primary_key = True, autoincrement= True)
    
    # Foreign key linking group order to the members of that specific group order
    group_id = db.Column('group_id', db.Integer, db.ForeignKey('group_order.group_id'), nullable = False)

    # Foreign key linking profile to the member of a group order
    profile_id = db.Column('profile_id', db.Integer, db.ForeignKey('profile.profile_id'), nullable=False)

    def __init__(self, name):
        self.name = name
        
    
