from app.models import Cart, User, db
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

def addToCart(data, current_user):
    user_email = current_user

    # Check if the user exists
    user = User.query.filter_by(email=user_email).first()
    if not user:
        return {'error': 'User does not exist'}, 404
    
    # Start a new transaction
    session = scoped_session(sessionmaker(bind=db.engine))
    
    try:
        items = data.get('data')
        for item in items:
            product_name = item.get('product_name')
            quantity = item.get('quantity')
            barcode = item.get('barcode')
            category = item.get('category')

            cart_item = Cart(
                user_email=user_email,
                barcode=barcode,
                product_name=product_name,
                category=category,
                quantity=quantity)
            session.add(cart_item)

        # Commit all the changes together
        session.commit()
        return {'message': 'Cart items added successfully'}
    except:
        # Rollback the transaction if any error occurs
        session.rollback()
        return {'error': 'Failed to add cart items'}, 500
    finally:
        session.close()

def getCartData(user_email):
    # Check if the user exists
    user = User.query.filter_by(email=user_email).first()
    if not user_email:
        return {'error': 'User does not exist'}, 404

    # Retrieve the user's cart items
    cart_items = Cart.query.filter_by(user_email=user.email).all()
    cart_items_data = [{'product_name': item.product_name, 'quantity': item.quantity, 'barcode': item.barcode, 'category': item.category}
                        for item in cart_items]
    return {'cart_items': cart_items_data}