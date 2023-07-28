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
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_email = db.Column(db.String(100), db.ForeignKey('users_db.email'), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, user_email, product_name, quantity, price):
        self.user_email = user_email
        self.product_name = product_name
        self.quantity = quantity
        self.price = price
    
@api.route('/cart', methods=['GET', 'POST'])
def cart():
    if request.method == 'POST':
        data = request.json
        user_email = data.get('user_email')
        product_name = data.get('product_name')
        quantity = data.get('quantity')
        price = data.get('price')

        # Check if the user exists
        user = User.query.filter_by(email=user_email).first()
        if not user:
            return {'error': 'User does not exist'}, 404

        cart_item = CartItem(
            user_email=user_email,
            item_name=product_name,
            item_price=price,
            # Add other attributes as needed
            quantity=quantity
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
        cart_items_data = [{'product_name': item.item_name, 'quantity': item.quantity, 'price': item.item_price}
                           for item in cart_items]
        return {'cart_items': cart_items_data}


if __name__ == '__main__':
    with api.app_context():  # Set up the application context
        db.create_all()      # Create the database tables
    api.run()