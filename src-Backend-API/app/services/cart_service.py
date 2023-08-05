from app.models import Cart, User,Product, db
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func ,text
from flask import jsonify


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

        # Commit all the changes together
        db.session.commit()
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

def get_cheapest_stores_with_cart_products(current_user_email, city):
    # Get the 5 cheapest stores with the total sum of all products in the cart for each store
    cart_items = Cart.query.filter_by(user_email=current_user_email).all()

    cheapest_stores_query = db.session.query(
        Product.chain_id, Product.sub_chain_id, Product.store_id,
        db.func.sum(Product.item_price * Product.quantity).label('total_amount')
    ).join(Cart, Cart.barcode == Product.item_code).filter(Product.city == city, Cart.user_email == current_user_email).group_by(Product.chain_id, Product.sub_chain_id, Product.store_id).order_by('total_amount').limit(5)

    cheapest_stores = cheapest_stores_query.all()

    results = []
    for store in cheapest_stores:
        chain_id, sub_chain_id, store_id, total_amount = store

        store_data = {
            'chain_id': chain_id,
            'sub_chain_id': sub_chain_id,
            'store_id': store_id,
            'total_amount': total_amount,
            'products': []
        }

        missing_item_codes = []

        for cart_item in cart_items:
            item_code = cart_item.barcode
            quantity = cart_item.quantity

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
                missing_item_codes.append(item_code)

                # Set default values for the missing item
                product_name = "Not Found"
                product_price = None
                product_total_price = 0

        # Add the list of missing item codes to the store_data
        store_data['missing_item_codes'] = missing_item_codes
        total_amount = sum(product['total_price'] for product in store_data['products'])
        store_data['total_amount'] = float(total_amount)
        results.append(store_data)


    return jsonify(results)


# def getCheapestStores(user_email, city):
#     # Retrieve the user's cart items
#     cart_items = Cart.query.filter_by(user_email=user_email).all()

#     # Get the list of products' barcode or name in the user's cart
#     products_data = [{'barcode': item.barcode, 'name': item.product_name} for item in cart_items]

#     # Retrieve the corresponding products from the products table
#     products_in_cart = db.session.query(func.min(Cart.product_name).label('product_name'), Cart.barcode).filter(
#         Cart.user_email == user_email,
#         func.coalesce(Cart.barcode, Cart.product_name).in_([item['barcode'] or item['name'] for item in products_data])
#     ).group_by(Cart.barcode).all()

#     # Get the barcode and name of products that exist in the cart
#     products_dict = {item.barcode: item.product_name for item in products_in_cart}

#     # Formulate the SQL query to search for stores with the products in the user's cart and within the specific city
#     query = text("""
#         SELECT s.chain_id, s.subchainid, s.storeid, s.storename, s.city, p.item_name, p.item_price
#         FROM products p
#         JOIN stores_table s ON p.chain_id = s.chain_id AND CAST(p.sub_chain_id AS BIGINT) = s.subchainid AND CAST(p.store_id AS BIGINT) = s.storeid
#         WHERE p.item_name IN :product_names
#         AND s.city = :city
#         GROUP BY s.chain_id, s.subchainid, s.storeid, p.item_name, p.item_price
#         HAVING SUM(p.quantity) >= 0.8 * (
#             SELECT SUM(c.quantity) 
#             FROM cart c
#             JOIN products p2 ON c.barcode = p2.item_code OR c.product_name = p2.item_name
#             WHERE c.user_email = :user_email 
#             AND p2.chain_id = s.chain_id
#             AND CAST(p2.sub_chain_id AS BIGINT) = s.subchainid
#             AND CAST(p2.store_id AS BIGINT) = s.storeid
#         )
#         ORDER BY p.item_price ASC
#         LIMIT 5
#     """)

#     # Execute the SQL query with the products, user_email, and city as parameters
#     product_names_tuple = tuple(products_dict.values())
#     cheapest_stores = db.session.execute(query, {
#         'product_names': product_names_tuple,
#         'user_email': user_email,
#         'city': city
#         })

#     # Process the results and get the cheapest stores with products and total amount to pay
#     stores_data = {}
#     for store in cheapest_stores:
#         store_key = (store.chain_id, store.subchainid, store.storeid)
#         if store_key not in stores_data:
#             stores_data[store_key] = {
#                 'chain_id': store.chain_id,
#                 'subchainid': store.subchainid,
#                 'storeid': store.storeid,
#                 'storename': store.storename,
#                 'city': store.city,
#                 'products': [],
#                 'total_amount': 0
#             }
#         stores_data[store_key]['products'].append({
#             'item_name': store.item_name,
#             'item_price': store.item_price
#         })
#         stores_data[store_key]['total_amount'] += store.item_price

#     return {'cheapest_stores': list(stores_data.values())}