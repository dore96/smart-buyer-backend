import json
from app.models import Cart, User,Product,Store, db
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_, desc
from decimal import Decimal

def save_cart(data, current_user):
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

        current_cart_barcodes = []

        for item in items:
            product_name = item.get('name')
            quantity = item.get('quantity')
            barcode = item.get('code')
            category = item.get('category')

            if barcode in existing_cart_items_dict:
                # Update the quantity of the existing cart item
                existing_cart_item = existing_cart_items_dict[barcode]
                existing_cart_item.quantity = quantity
            else:
                # Add a new cart item
                cart_item = Cart(
                    user_email=user_email,
                    barcode=barcode,
                    product_name=product_name,
                    category=category,
                    quantity=int(quantity))
                db.session.add(cart_item)

            current_cart_barcodes.append(barcode)
        
        # Remove cart items not in the data
        for barcode in existing_cart_items_dict:
            if barcode not in current_cart_barcodes:
                db.session.delete(existing_cart_items_dict[barcode])

        # Commit all the changes together
        db.session.commit()
        db.session.close()
        return {'message': 'Cart items updated/added successfully'}
    except IntegrityError:
        # Handle any integrity constraint violation (e.g., duplicate barcodes)
        db.session.rollback()
        return {'error': 'Failed to update/add cart items. Integrity constraint violation.'}, 500
    except Exception as e:
        # Log any other exceptions that occurred during the process
        print('An error occurred while updating/adding cart items: %s', e)
        db.session.rollback()
        return {'error': 'Failed to update/add cart items'}, 500
    finally:
        db.session.close()

def get_cart_data(user_email):
    session = db.session # Create a session
    # Check if the user exists
    user = session.query(User).filter_by(email=user_email).first()
    if not user_email:
        session.close() 
        return {'error': 'User does not exist'}, 404

    # Retrieve the user's cart items
    cart_items = Cart.query.filter_by(user_email=user.email).all()
    cart_items_data = [{'id': item.barcode , 'name': item.product_name, 'quantity': item.quantity, 'code': item.barcode, 'category': item.category}
                        for item in cart_items]
    session.close() 
    return {'cart_items': cart_items_data}
            
def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def get_store_details(chain_id, sub_chain_id, store_id):
    """
    Retrieve store details for a specific store based on chain ID, sub-chain ID, and store ID.

    Args:
        chain_id (str): The unique identifier for the chain.
        sub_chain_id (int): The unique identifier for the sub-chain.
        store_id (int): The unique identifier for the store.

    Returns:
        dict or None: A dictionary containing store details (chainname, subchainname, storename, address, city, zipcode)
        if the store is found, or None if the store does not exist.
    """
    store = Store.query.filter_by(chain_id=chain_id, subchainid=sub_chain_id, storeid=store_id).first()
    if store:
        return {
            'chainname': store.chainname,
            'subchainname': store.subchainname,
            'storename': store.storename,
            'address': store.address,
            'city': store.city,
            'zipcode': store.zipcode
        }
    return None

def get_cheapest_stores_with_cart_products(current_user_email, city):
    """
    Retrieve a list of cheapest stores with cart products for a specific user and city.

    Args:
        current_user_email (str): The email address of the current user.
        city (str): The name of the city to search for stores.

    Returns:
        list: A list of dictionaries containing store data, including chain ID, sub-chain ID, store ID,
        total amount, and a list of products and their details.
    """
    cart_items = Cart.query.filter_by(user_email=current_user_email).all()
    barcode_join_condition = Cart.barcode == Product.item_code
    product_name_join_condition = Cart.product_name == Product.item_name
    join_condition = or_(barcode_join_condition, product_name_join_condition)

    # Query the database to find the cheapest stores based on cart items
    cheapest_stores_query = db.session.query(
        Product.chain_id, Product.sub_chain_id, Product.store_id,
        db.func.sum(Product.item_price * Cart.quantity).label('total_amount'),
        db.func.count().label('items_count')
    ).join(Cart, join_condition).filter(
        Product.city == city,
        Cart.user_email == current_user_email
    ).group_by(Product.chain_id, Product.sub_chain_id, Product.store_id).order_by(desc('items_count'), 'total_amount').limit(5)

    # Process each cheapest store and its associated cart items
    cheapest_stores = cheapest_stores_query.all()
    results = []
    for store in cheapest_stores:
        chain_id, sub_chain_id, store_id, total_amount, number_of_existing_products = store

        store_data = {
            'chain_id': chain_id,
            'sub_chain_id': sub_chain_id,
            'store_id': store_id,
            'total_amount': total_amount,
            'products': [],
            'missing_item_codes': []
        }

        # Iterate through the user's cart items
        for cart_item in cart_items:
            item_name = cart_item.product_name
            item_code = cart_item.barcode
            quantity = cart_item.quantity

            # Query the product details for the cart item
            product_price_query = db.session.query(Product.item_name, Product.item_price).filter(Product.city == city, Product.chain_id == chain_id, Product.sub_chain_id == sub_chain_id, Product.store_id == store_id, Product.item_code == item_code)
            result = product_price_query.first()

            if result is not None:
                product_name, product_price = result
                product_total_price = product_price * quantity
                store_data['products'].append({
                    'product_name': product_name,
                    'product_price': float(product_price) if product_price is not None else None,
                    'quantity': quantity,
                    'total_price': float(product_total_price)
                })
            else:
                # If no matching product is found, add its item_code to the list of missing item codes
                store_data['missing_item_codes'].append(item_name)

        results.append(store_data)

    # Fetch store details for each cheap store and add them to the store data
    for store_data in results:
        store_details = get_store_details(store_data['chain_id'], store_data['sub_chain_id'], store_data['store_id'])
        if store_details:
            store_data.update(store_details)

     # Use json.dumps() with indent parameter to present the JSON response with indentation
    formatted_response = json.dumps(results, indent=4, ensure_ascii=False, default=decimal_default)
    # Convert the cleaned string to a Python object
    cheapest_stores_data = json.loads(formatted_response)

    return cheapest_stores_data