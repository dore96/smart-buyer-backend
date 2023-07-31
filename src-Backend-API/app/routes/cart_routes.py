from flask import Blueprint, request, jsonify
from app.services.cart_service import addToCart, getCartData
from flask_jwt_extended import jwt_required, get_jwt_identity

cart_api = Blueprint('cart_api', __name__)

@cart_api.route('/cart', methods=['GET', 'POST'])
@jwt_required() 
def cart():
    current_user_email = get_jwt_identity()
    if request.method == 'POST':
        data = request.json
        return addToCart(data,current_user_email)

    if request.method == 'GET':
        return getCartData(current_user_email)