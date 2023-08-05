from flask import Blueprint, request, jsonify
from app.services.cart_service import addToCart, getCartData,get_cheapest_stores_with_cart_products
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
    
@cart_api.route('/cart/calculate', methods=['GET'])
@jwt_required() 
def cart_calculation():
    try:
        current_user_email = get_jwt_identity()
        data = request.json
        if not data:
            return {'error': 'Request data not provided or not in valid JSON format'}, 400

        city = data.get('city')
        cart_items = data.get('data')
        # Validate if city and cart_items are present in the request
        if not city or not cart_items:
            return {'error': 'City and cart items data not provided in the request'}, 400

        # Update cart items for the user
        response = addToCart(data, current_user_email)

        # Calculate cheapest stores with 80%+ of the products in the user's cart within the specific city
        cheapest_stores = get_cheapest_stores_with_cart_products(current_user_email, city)

        return {'message': response['message'], 'cheapest_stores': cheapest_stores}
    
    except Exception as e:
        # Log any exceptions that occurred during the process
        print('An error occurred while processing the request:', e)
        return {'error': 'Failed to process the request'}, 500