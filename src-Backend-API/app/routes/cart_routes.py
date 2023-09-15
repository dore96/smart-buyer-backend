from flask import Blueprint, request
from app.services.cart_service import save_cart, get_cart_data,get_cheapest_stores_with_cart_products
from flask_jwt_extended import jwt_required, get_jwt_identity

# Create a Flask Blueprint for the cart API
cart_api = Blueprint('cart_api', __name__)

# Route for handling cart operations (GET and POST)
@cart_api.route('/cart', methods=['GET', 'POST'])
@jwt_required() 
def cart():
    """
    Endpoint for managing user shopping cart.

    - GET: Retrieve the user's cart data.
    - POST: Save or update the user's cart data.

    Returns:
        JSON response containing cart data or success message.
    """
    current_user_email = get_jwt_identity()
    if request.method == 'POST':
        data = request.json
        return save_cart(data,current_user_email)

    if request.method == 'GET':
        return get_cart_data(current_user_email)
    

# Route for cart calculation
@cart_api.route('/cart/calculate', methods=['POST'])
@jwt_required() 
def cart_calculation():
    """
    Endpoint for cart calculation, including finding the cheapest stores.

    - POST: Calculate the cheapest stores based on user's cart and city.

    Returns:
        JSON response containing cart calculation results.
    """
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
        response = save_cart(data, current_user_email)

        # Calculate cheapest stores with 80%+ of the products in the user's cart within the specific city
        cheapest_stores = get_cheapest_stores_with_cart_products(current_user_email, city)

        return {'message': response['message'], 'cheapest_stores': cheapest_stores}
    
    except Exception as e:
        # Log any exceptions that occurred during the process
        print('An error occurred while processing the request:', e)
        return {'error': 'Failed to process the request'}, 500