from app.models import Product,Store, db
from sqlalchemy import func

CHAIN_NAME_FIELD = 'chain_name'
CHAIN_ID_FIELD = 'chain_id'
STORES_FIELD = 'stores'
SUB_CHAINS_FIELD = 'subchains'
SUB_CHAIN_ID_FIELD = 'sub_chain_id'
SUB_CHAIN_NAME_FIELD = 'sub_chain_name'

def get_chains_ids():
    # Query the stores_table to get all chains and their data
    chains = db.session.query(
        Store.chain_id,
        Store.chainname,
        Store.subchainid,
        Store.subchainname,
        Store.storeid,
        Store.storename,
        Store.address,
        Store.city,
        Store.zipcode
    ).all()

    # Create a dictionary to store the chains and their data
    chain_data = {}
    for chain_id, chain_name, sub_chain_id, sub_chain_name, store_id, store_name, address, city, zipcode in chains:
        # If the chain is not already in the dictionary, add it
        if chain_id not in chain_data:
            chain_data[chain_id] = {
                'chain_name': chain_name,
                SUB_CHAINS_FIELD: {}
            }

        # If the subchain is not already in the dictionary, add it
        if sub_chain_id not in chain_data[chain_id][SUB_CHAINS_FIELD]:
            chain_data[chain_id][SUB_CHAINS_FIELD][sub_chain_id] = {
                'sub_chain_name': sub_chain_name,
                'stores': {}
            }

        # Add the store data to the subchain's stores
        chain_data[chain_id][SUB_CHAINS_FIELD][sub_chain_id]['stores'][store_id] = {
            'store_name': store_name,
            'store_id': store_id,
            'address': address,
            'city': city,
            'zipcode': zipcode
        }

    return chain_data

def get_store_data(store):
    return({
            'store_id': store.storeid,
            'store_name': store.storename,
            'address': store.address,
            'city': store.city,
            'zipcode': store.zipcode,
            'chain_id': store.chain_id,
            'sub_chain_id': store.subchainid
            })

def get_sub_chain_data(store):
    return ({
                SUB_CHAIN_ID_FIELD: store.subchainid,
                SUB_CHAIN_NAME_FIELD: store.subchainname,
                STORES_FIELD: []
            })

def get_store_data_by_chain(chain_id):
    # Query the stores_table to get all stores for the specified chain_id
    stores = Store.query.filter_by(chain_id=chain_id).all()

    # Create a dictionary to store chain data
    chain_data = {
        CHAIN_ID_FIELD: chain_id,
        CHAIN_NAME_FIELD: '',
        SUB_CHAINS_FIELD: []
    }

    for store in stores:
        if not chain_data[CHAIN_NAME_FIELD]:
            # Set the chain name (it will be the same for all stores in the chain)
            chain_data[CHAIN_NAME_FIELD] = store.chainname

        # Check if the subchain already exists in the chain_data['subchains'] list
        subchain_exists = False
        for subchain_data in chain_data[SUB_CHAINS_FIELD]:
            if subchain_data[SUB_CHAIN_NAME_FIELD] == store.subchainname:
                store_data = get_store_data(store)
                subchain_data[STORES_FIELD].append(store_data)
                subchain_exists = True
                break

        if not subchain_exists:
            # If the subchain does not exist, create a new subchain entry
            subchain_data = get_sub_chain_data(store)
            store_data = get_store_data(store)
            subchain_data[STORES_FIELD].append(store_data)
            chain_data[SUB_CHAINS_FIELD].append(subchain_data)

    return chain_data

def get_store_data_by_city(city_name):
    # Query the stores_table to get all stores for the specified city_name
    stores = Store.query.filter(Store.city.like(f'%{city_name}%')).all()

    # Create a dictionary to store city data
    city_data = {
        'city_name': city_name,
        'chains': []
    }

    for store in stores:
        # Check if the chain already exists in the city_data['chains'] list
        chain_exists = False
        for chain_data in city_data['chains']:
            if chain_data[CHAIN_ID_FIELD] == store.chain_id:
                # Check if the subchain already exists in the chain_data['subchains'] list
                subchain_exists = False
                for subchain_data in chain_data[SUB_CHAINS_FIELD]:
                    if subchain_data[SUB_CHAIN_ID_FIELD] == store.subchainid:
                        store_data = get_store_data(store)
                        subchain_data[STORES_FIELD].append(store_data)
                        subchain_exists = True
                        break

                if not subchain_exists:
                    # If the subchain does not exist, create a new subchain entry
                    subchain_data = get_sub_chain_data(store)
                    store_data = get_store_data(store)
                    subchain_data[STORES_FIELD].append(store_data)
                    chain_data[SUB_CHAINS_FIELD].append(subchain_data)

                chain_exists = True
                break

        if not chain_exists:
            # If the chain does not exist, create a new chain entry
            chain_data = {
                CHAIN_ID_FIELD: store.chain_id,
                CHAIN_NAME_FIELD: store.chainname,
                SUB_CHAINS_FIELD: []
            }
            subchain_data = get_sub_chain_data(store)
            store_data = get_store_data(store)
            subchain_data[STORES_FIELD].append(store_data)
            chain_data[SUB_CHAINS_FIELD].append(subchain_data)
            city_data['chains'].append(chain_data)

    return city_data

def get_product_data_by_barcode(barcode):
    # Subquery to get the item_price range for the given barcode
    price_subquery = db.session.query(
        func.min(Product.item_price).label('min_price'),
        func.max(Product.item_price).label('max_price')
    ).filter(Product.item_code == barcode).subquery()

    # Main query to get the first occurrence of the product with the given barcode
    product_data = db.session.query(
        Product.item_name,
        price_subquery.c.min_price,
        price_subquery.c.max_price,
        Product.item_code,
        Product.manufacturer_item_description,
        Product.unit_qty,
        Product.item_type,
        Product.manufacturer_name,
        Product.manufacture_country,
        Product.unit_of_measure,
        Product.quantity,
        Product.qty_in_package,
        Product.unit_of_measure_price,
    ).filter(Product.item_code == barcode).first()

    if product_data:
        product_dict = {
            'item_name': product_data[0],
            'min_item_price': product_data[1],
            'max_item_price': product_data[2],
            'item_code': product_data[3],
            'manufacturer_item_description': product_data[4],
            'unit_qty': product_data[5],
            'item_type': product_data[6],
            'manufacturer_name': product_data[7],
            'manufacture_country': product_data[8],
            'unit_of_measure': product_data[9],
            'quantity': product_data[10],
            'qty_in_package': product_data[11],
            'unit_of_measure_price': product_data[12]
        }
    return product_dict

def get_product_data_by_name(product_name):
    # Query all products with the given name
    products = Product.query.filter(Product.item_name.ilike(f'%{product_name}%')).all()

    if products:
        # Group products by name and barcode
        grouped_products = {}
        for product in products:
            # Group by name
            if product.item_name not in grouped_products:
                grouped_products[product.item_name] = {
                    'item_name': product.item_name,
                    'item_price_min': product.item_price,
                    'item_price_max': product.item_price,
                    'item_code': product.item_code,
                    'manufacturer_item_description': product.manufacturer_item_description,
                    'unit_qty': product.unit_qty,
                    'item_type': product.item_type,
                    'manufacturer_name': product.manufacturer_name,
                    'manufacture_country': product.manufacture_country,
                    'unit_of_measure': product.unit_of_measure,
                    'quantity': product.quantity,
                    'qty_in_package': product.qty_in_package,
                    'unit_of_measure_price': product.unit_of_measure_price
                }
            else:
                # Update price range if necessary
                if product.item_price < grouped_products[product.item_name]['item_price_min']:
                    grouped_products[product.item_name]['item_price_min'] = product.item_price
                elif product.item_price > grouped_products[product.item_name]['item_price_max']:
                    grouped_products[product.item_name]['item_price_max'] = product.item_price

    return list(grouped_products.values())