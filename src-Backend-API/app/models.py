from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, primary_key=True)
    password = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"User: {self.first_name} {self.last_name} ({self.email})"

    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.set_password(password)  # Hash the password and store it

    def set_password(self, password):
        # Hash the provided password and store it in the password field
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

class Cart(db.Model):
    __tablename__ = 'cart'
    user_email = db.Column(db.String(100), db.ForeignKey('users.email'), nullable=False, primary_key=True)
    barcode = db.Column(db.Integer,nullable=False,primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, user_email, barcode, product_name,category, quantity ):
        self.user_email = user_email
        self.barcode = barcode
        self.product_name = product_name
        self.quantity = quantity
        self.category = category
