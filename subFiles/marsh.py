from flask_marshmallow  import Marshmallow
from marshmallow import Schema, fields
from subFiles.config import app

#Init marshmallow
ma = Marshmallow(app)

 #Product Schema
class ProfileSchema(ma.Schema):
    profile_id = fields.Integer()
    username = fields.String()
    email = fields.String()
    created_at = fields.String()
    
    # class Meta:
    #     fields = ('profile_id', 'username','first_name', 'last_name' 'email', 'password', 'created_at')


class AddOnSchema(ma.Schema):
    drink_id = fields.Integer()
    number_of_sugar_bags = fields.Integer()
    milk_texture = fields.String()
    extra_comments = fields.String()
    
    # class Meta:
    #     fields = ('drink_id', 'number_of_sugar_bags', 'milk_texture', 'extra_comments')
        
class DrinkSchema(ma.Schema):
    drink_id = fields.Integer()
    name = fields.String()
    is_hot = fields.String()
    bean_type = fields.String()
    roast_type = fields.String()
    drink_type = fields.String()
    creamer_type = fields.String()
    sugar_type = fields.String()    
    milk_type = fields.String()    
    drink_location = fields.String()    
    profile_id = fields.Integer()    
    created_at = fields.DateTime()
    add_ons = fields.Nested(AddOnSchema)
    
    # class Meta:
    #     fields = ('drink_id', 'name', 'is_hot', 'bean_type', 'roast_type', 'drink_type',
    #      'creamer_type', 'sugar_type', 'milk_type', 'drink_location', 'profile_id', 'created_at')
    #     add_ons = fields.Nested(AddOnSchema)

class FriendSchema(ma.Schema):
    friend_id = fields.Integer()
    friend_Username = fields.String()
    profile_id = fields.Integer()
    

    # class Meta:
    #     fields = ('friend_Id', 'friend_Username', 'profile_id')
        
class GroupOrderSchema(ma.Schema):
    group_id = fields.Integer()
    is_active = fields.Boolean()
    is_admin = fields.String()
    members = fields.Integer()
    order_location = fields.Integer()
    order_time = fields.String()
    created_at = fields.DateTime()
    
    # class Meta:
    #     fields = ('group_id', 'is_admin', 'members', 'order_location', 'order_time', 'created_at')
        
class MembersSchema(ma.Schema):
    member_id = fields.Integer()
    group_id = fields.Integer()
    profile_id = fields.Integer()
    
    # class Meta:
    #     fields = ('member_id', 'group_id', 'profile_id')

# Init Schema
profile_schema = ProfileSchema()
profiles_schema = ProfileSchema(many=True)

drink_schema = DrinkSchema()
drinks_schema = DrinkSchema(many=True)

addOn_schema = AddOnSchema()
addOns_schema = AddOnSchema(many=True)

friend_schema = FriendSchema()
friends_schema = FriendSchema(many=True)

groupOrder_schema = GroupOrderSchema()
groupOrders_schema = GroupOrderSchema(many=True)

member_schema = MembersSchema()
members_schema = MembersSchema(many=True)

