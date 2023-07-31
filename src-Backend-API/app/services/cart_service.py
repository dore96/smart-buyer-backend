from app.models import Cart, User, db
from sqlalchemy.exc import IntegrityError

def addToCart(data, current_user):
    user_email = current_user

    # Check if the user exists
    user = User.query.filter_by(email=user_email).first()
    if not user:
        return {'error': 'User does not exist'}, 404

    try:
        items = data.get('data')

        # Retrieve existing cart items for the user
        existing_cart_items = Cart.query.filter_by(user_email=user_email).all()
        existing_cart_items_dict = {item.barcode: item for item in existing_cart_items}

        for item in items:
            product_name = item.get('product_name')
            quantity = item.get('quantity')
            barcode = item.get('barcode')
            category = item.get('category')

            if int(barcode) in existing_cart_items_dict:
                # Update the quantity of the existing cart item
                existing_cart_item = existing_cart_items_dict[int(barcode)]
                existing_cart_item.quantity = quantity
            else:
                # Add a new cart item
                cart_item = Cart(
                    user_email=user_email,
                    barcode=int(barcode),
                    product_name=product_name,
                    category=category,
                    quantity=quantity)
                db.session.add(cart_item)

        # Commit all the changes together
        db.session.commit()
        return {'message': 'Cart items updated/added successfully'}
    except IntegrityError:
        # Handle any integrity constraint violation (e.g., duplicate barcodes)
        db.session.rollback()
        return {'error': 'Failed to update/add cart items. Integrity constraint violation.'}, 500
    except Exception as e:
        # Log any other exceptions that occurred during the process
        db.session.rollback()
        return {'error': 'Failed to update/add cart items'}, 500
    finally:
        db.session.close()

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