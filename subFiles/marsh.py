from flask_marshmallow  import Marshmallow
from subFiles.config import app

#Init marshmallow
ma = Marshmallow(app)

 #Product Schema
class ProfileSchema(ma.Schema):
    class Meta:
        fields = ('profile_id', 'username','first_name', 'last_name' 'email', 'password', 'created_at')
        
class DrinkSchema(ma.Schema):
    class Meta:
        fields = ('drink_id', 'name', 'is_hot', 'bean_type', 'roast_type', 'drink_type',
         'creamer_type', 'sugar_type', 'milk_type', 'drink_location', 'profile_id', 'created_at')


class AddOnSchema(ma.Schema):
    class Meta:
        fields = ('drink_id', 'number_of_sugar_bags', 'milk_texture', 'milk_level', 'extra_comments')

class FriendSchema(ma.Schema):
    class Meta:
        fields = ('friend_Id', 'friend_Username', 'profile_id')
        
class GroupOrderSchema(ma.Schema):
    class Meta:
        fields = ('group_id', 'is_admin', 'members', 'order_location', 'order_time', 'created_at')
        
class MembersSchema(ma.Schema):
    class Meta:
        fields = ('member_id', 'group_id', 'profile_id')

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

