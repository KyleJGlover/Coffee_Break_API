from flask_marshmallow  import Marshmallow
from marshmallow import Schema, fields
from subFiles.config import app

#Init marshmallow
ma = Marshmallow(app)

 #Product Schema
class ProfileSchema(ma.Schema):
    profile_id = fields.Integer()
    username = fields.String()
    first_name = fields.String()
    last_name = fields.String()
    description = fields.String()
    email = fields.String()
    
    # class Meta:
    #     fields = ('profile_id', 'username','first_name', 'last_name' 'email', 'password', 'created_at')


# class AddOnSchema(ma.Schema):
#     drink_id = fields.Integer()
#     number_of_sugar_bags = fields.Integer()
#     milk_texture = fields.String()
#     extra_comments = fields.String()
    
    # class Meta:
    #     fields = ('drink_id', 'number_of_sugar_bags', 'milk_texture', 'extra_comments')
        
class DrinkSchema(ma.Schema):
    drink_id = fields.Integer()
    name = fields.String()
    temperature = fields.String()
    bean_type = fields.String()
    roast_type = fields.String()
    drink_type = fields.String()
    creamer_type = fields.String()
    sugar_type = fields.String()    
    milk_type = fields.String()
    flavor = fields.String()   
    drink_location = fields.String()    
    profile_id = fields.Integer()    
    is_favorite = fields.Boolean()
    number_of_sugar_bags = fields.Integer()
    isSteamed = fields.Boolean()
    extra_comments = fields.String()
    room_for_creamer = fields.Boolean()
    room_for_milk = fields.Boolean()
    
    # class Meta:
    #     fields = ('drink_id', 'name', 'is_hot', 'bean_type', 'roast_type', 'drink_type',
    #      'creamer_type', 'sugar_type', 'milk_type', 'drink_location', 'profile_id', 'created_at')
    #     add_ons = fields.Nested(AddOnSchema)

class FriendSchema(ma.Schema):
    friend_id = fields.Integer()
    user_a = fields.Integer()
    user_b = fields.Integer()

    # class Meta:
    #     fields = ('friend_Id', 'friend_Username', 'profile_id')
        
class GroupOrderSchema(ma.Schema):
    date = fields.String()
    name = fields.String()
    group_id = fields.Integer()
    is_active = fields.Boolean()
    admin = fields.String()
    order_location = fields.String()
    order_time = fields.String()
    address = fields.String()
    
    # class Meta:
    #     fields = ('name','group_id', 'is_admin', 'is_active', 'order_location', 'order_time', 'created_at')
        
class MembersSchema(ma.Schema):
    member_id = fields.Integer()
    group_id = fields.Integer()
    username = fields.String()
    coffee = fields.String()
    
    # class Meta:
    #     fields = ('member_id', 'group_id', 'username')

# Init Schema
profile_schema = ProfileSchema()
profiles_schema = ProfileSchema(many=True)

drink_schema = DrinkSchema()
drinks_schema = DrinkSchema(many=True)

# addOn_schema = AddOnSchema()
# addOns_schema = AddOnSchema(many=True)

friend_schema = FriendSchema()
friends_schema = FriendSchema(many=True)

groupOrder_schema = GroupOrderSchema()
groupOrders_schema = GroupOrderSchema(many=True)

member_schema = MembersSchema()
members_schema = MembersSchema(many=True)

