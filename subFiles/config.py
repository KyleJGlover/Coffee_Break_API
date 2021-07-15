from flask import Flask, request, jsonify
# Creating the object like structure of the models and formulates SQL queries
from flask_sqlalchemy import SQLAlchemy
import os
from flask_bcrypt import Bcrypt

# Init app 
app = Flask(__name__)

bcrypt = Bcrypt(app)
basedir = os.path.abspath(os.path.dirname(__file__))

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'itsasecret'


