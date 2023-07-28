from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS 

api = Flask(__name__)
api.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:De9654@localhost:5432/users'
db = SQLAlchemy(api)

# Enable CORS for all routes
CORS(api)

class User(db.Model):
    __tablename__ = 'users_db'  
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False,primary_key=True)
    password = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"User: {self.first_name} {self.last_name} ({self.email})"

    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password

def format_user(user):
    return {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "created_at": user.created_at
    }

# create a user
@api.route('/user', methods=['POST'])
def createUser():
    data = request.json
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    password = data.get('password')

    # Check if a user with the same email already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return {'error': 'User with this email already exists'}, 409

    user = User(first_name=first_name, last_name=last_name, email=email, password=password)
    db.session.add(user)
    db.session.commit()
    return format_user(user)

class CartItem(db.Model):
    __tablename__ = 'cart_items'
    user_email = db.Column(db.String(100), db.ForeignKey('users_db.email'), nullable=False)
    item_name = db.Column(db.TEXT, nullable=False)
    item_price = db.Column(db.NUMERIC, nullable=False)
    item_code = db.Column(db.TEXT, primary_key=True)
    manufacturer_item_description = db.Column(db.TEXT)
    price_update_date = db.Column(db.TIMESTAMP)
    unit_qty = db.Column(db.TEXT)
    item_type = db.Column(db.INT)
    manufacturer_name = db.Column(db.TEXT)
    manufacture_country = db.Column(db.TEXT)
    unit_of_measure = db.Column(db.TEXT)
    quantity = db.Column(db.INT, nullable=False)
    b_is_weighted = db.Column(db.INT)
    qty_in_package = db.Column(db.INT)
    unit_of_measure_price = db.Column(db.NUMERIC)
    allow_discount = db.Column(db.INT)
    item_status = db.Column(db.INT)
    last_update_date = db.Column(db.TEXT)
    last_update_time = db.Column(db.TEXT)

    def __repr__(self):
        return f"CartItem: {self.item_name} (User: {self.user_email})"
    
@api.route('/cart', methods=['GET', 'POST'])
def cart():
    if request.method == 'POST':
        data = request.json
        user_email = data.get('user_email')
        product_name = data.get('product_name')
        quantity = data.get('quantity')
        price = data.get('price')
        item_code = data.get('item_code')
        manufacturer_item_description = data.get('manufacturer_item_description')
        price_update_date = data.get('price_update_date')
        unit_qty = data.get('unit_qty')
        item_type = data.get('item_type')
        manufacturer_name = data.get('manufacturer_name')
        manufacture_country = data.get('manufacture_country')
        unit_of_measure = data.get('unit_of_measure')
        b_is_weighted = data.get('b_is_weighted')
        qty_in_package = data.get('qty_in_package')
        unit_of_measure_price = data.get('unit_of_measure_price')
        allow_discount = data.get('allow_discount')
        item_status = data.get('item_status')
        last_update_date = data.get('last_update_date')
        last_update_time = data.get('last_update_time')

        # Check if the user exists
        user = User.query.filter_by(email=user_email).first()
        if not user:
            return {'error': 'User does not exist'}, 404

        cart_item = CartItem(
            user_email=user_email,
            item_name=product_name,
            item_price=price,
            item_code=item_code,
            manufacturer_item_description=manufacturer_item_description,
            price_update_date=price_update_date,
            unit_qty=unit_qty,
            item_type=item_type,
            manufacturer_name=manufacturer_name,
            manufacture_country=manufacture_country,
            unit_of_measure=unit_of_measure,
            quantity=quantity,
            b_is_weighted=b_is_weighted,
            qty_in_package=qty_in_package,
            unit_of_measure_price=unit_of_measure_price,
            allow_discount=allow_discount,
            item_status=item_status,
            last_update_date=last_update_date,
            last_update_time=last_update_time
        )
        db.session.add(cart_item)
        db.session.commit()
        return {'message': 'Cart item added successfully'}

    if request.method == 'GET':
        user_email = request.args.get('user_email')

        # Check if the user exists
        user = User.query.filter_by(email=user_email).first()
        if not user:
            return {'error': 'User does not exist'}, 404

        # Retrieve the user's cart items
        cart_items = CartItem.query.filter_by(user_email=user_email).all()
        cart_items_data = [{'product_name': item.item_name,
                            'quantity': item.quantity,
                            'price': item.item_price,
                            'item_code': item.item_code,
                            'manufacturer_item_description': item.manufacturer_item_description,
                            'price_update_date': item.price_update_date,
                            'unit_qty': item.unit_qty,
                            'item_type': item.item_type,
                            'manufacturer_name': item.manufacturer_name,
                            'manufacture_country': item.manufacture_country,
                            'unit_of_measure': item.unit_of_measure,
                            'b_is_weighted': item.b_is_weighted,
                            'qty_in_package': item.qty_in_package,
                            'unit_of_measure_price': item.unit_of_measure_price,
                            'allow_discount': item.allow_discount,
                            'item_status': item.item_status,
                            'last_update_date': item.last_update_date,
                            'last_update_time': item.last_update_time}
                           for item in cart_items]
        return {'cart_items': cart_items_data}


if __name__ == '__main__':
    with api.app_context():  # Set up the application context
        db.create_all()      # Create the database tables
    api.run()