from flask import Blueprint, request, jsonify
from app.models import CartItem, User
from app.services.cart_service import addToCart, getCartData

cart_api = Blueprint('cart_api', __name__)

@cart_api.route('/cart', methods=['GET', 'POST'])
def cart():
    if request.method == 'POST':
        data = request.json
        return addToCart(data)

    if request.method == 'GET':
        return getCartData(request)