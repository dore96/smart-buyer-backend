from app.models import CartItem, User, db

def addToCart(data):
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


    
def getCartData(request):
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