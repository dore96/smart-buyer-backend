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
    barcode = db.Column(db.String(20),nullable=False,primary_key=True)
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

class Product(db.Model):
    __tablename__ = 'products'

    city = db.Column(db.TEXT)
    chain_id = db.Column(db.TEXT, primary_key=True)
    sub_chain_id = db.Column(db.INT, primary_key=True)
    store_id = db.Column(db.INT, primary_key=True)
    item_name = db.Column(db.TEXT)
    item_price = db.Column(db.NUMERIC)
    item_code = db.Column(db.TEXT, primary_key=True)
    manufacturer_item_description = db.Column(db.TEXT)
    price_update_date = db.Column(db.TIMESTAMP)
    unit_qty = db.Column(db.TEXT)
    item_type = db.Column(db.INT)
    manufacturer_name = db.Column(db.TEXT)
    manufacture_country = db.Column(db.TEXT)
    unit_of_measure = db.Column(db.TEXT)
    quantity = db.Column(db.NUMERIC)
    b_is_weighted = db.Column(db.INT)
    qty_in_package = db.Column(db.NUMERIC)
    unit_of_measure_price = db.Column(db.NUMERIC)
    allow_discount = db.Column(db.INT)
    item_status = db.Column(db.INT)
    last_update_date = db.Column(db.TEXT)
    last_update_time = db.Column(db.TEXT)

    def __repr__(self):
        return f"Product(city='{self.city}', chain_id='{self.chain_id}', sub_chain_id={self.sub_chain_id}, store_id={self.store_id}, item_name='{self.item_name}', item_code='{self.item_code}')"
    
class Store(db.Model):
    __tablename__ = 'stores_table'

    chainname = db.Column(db.String(255), nullable=False)
    subchainname = db.Column(db.String(255), nullable=False)
    storename = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(255), nullable=False)
    zipcode = db.Column(db.BigInteger, nullable=False)
    chain_id = db.Column(db.String(255), primary_key=True)
    subchainid = db.Column(db.BigInteger, primary_key=True)
    storeid = db.Column(db.BigInteger, primary_key=True)

    def __init__(self, chainname, subchainname, storename, address, city, zipcode, chain_id, subchainid, storeid):
        self.chainname = chainname
        self.subchainname = subchainname
        self.storename = storename
        self.address = address
        self.city = city
        self.zipcode = zipcode
        self.chain_id = chain_id
        self.subchainid = subchainid
        self.storeid = storeid