from app.models import Cart, User,Product,Store, db

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
    for chain_id, chainname, subchainid, subchainname, storeid, storename, address, city, zipcode in chains:
        # If the chain is not already in the dictionary, add it
        if chain_id not in chain_data:
            chain_data[chain_id] = {
                'chainname': chainname,
                'subchains': {}
            }

        # If the subchain is not already in the dictionary, add it
        if subchainid not in chain_data[chain_id]['subchains']:
            chain_data[chain_id]['subchains'][subchainid] = {
                'subchainname': subchainname,
                'stores': {}
            }

        # Add the store data to the subchain's stores
        chain_data[chain_id]['subchains'][subchainid]['stores'][storeid] = {
            'storename': storename,
            'address': address,
            'city': city,
            'zipcode': zipcode
        }

    return chain_data

def get_store_data_by_chain(chain_id):
    # Query the stores_table to get all stores for the specified chain_id
    stores = Store.query.filter_by(chain_id=chain_id).all()

    # Create a dictionary to store chain data
    chain_data = {
        'chain_id': chain_id,
        'chain_name': '',
        'subchains': []
    }

    for store in stores:
        if not chain_data['chain_name']:
            # Set the chain name (it will be the same for all stores in the chain)
            chain_data['chain_name'] = store.chainname

        # Check if the subchain already exists in the chain_data['subchains'] list
        subchain_exists = False
        for subchain_data in chain_data['subchains']:
            if subchain_data['sub_chain_name'] == store.subchainname:
                store_data = {
                    'store_id': store.storeid,
                    'store_name': store.storename,
                    'address': store.address,
                    'city': store.city,
                    'zipcode': store.zipcode,
                    'chain_id': store.chain_id,
                    'sub_chain_id': store.subchainid
                }
                subchain_data['stores'].append(store_data)
                subchain_exists = True
                break

        if not subchain_exists:
            # If the subchain does not exist, create a new subchain entry
            subchain_data = {
                'sub_chain_id': store.subchainid,
                'sub_chain_name': store.subchainname,
                'stores': []
            }
            store_data = {
                'store_id': store.storeid,
                'store_name': store.storename,
                'address': store.address,
                'city': store.city,
                'zipcode': store.zipcode,
                'chain_id': store.chain_id,
                'sub_chain_id': store.subchainid
            }
            subchain_data['stores'].append(store_data)
            chain_data['subchains'].append(subchain_data)

    return chain_data

def get_store_data_by_city(city_name):
    # Query the stores_table to get all stores for the specified city_name
    stores = Store.query.filter_by(city=city_name).all()

    # Create a dictionary to store city data
    city_data = {
        'city_name': city_name,
        'chains': []
    }

    for store in stores:
        # Check if the chain already exists in the city_data['chains'] list
        chain_exists = False
        for chain_data in city_data['chains']:
            if chain_data['chain_id'] == store.chain_id:
                # Check if the subchain already exists in the chain_data['subchains'] list
                subchain_exists = False
                for subchain_data in chain_data['subchains']:
                    if subchain_data['sub_chain_id'] == store.subchainid:
                        store_data = {
                            'store_id': store.storeid,
                            'store_name': store.storename,
                            'address': store.address,
                            'zipcode': store.zipcode,
                            'sub_chain_id': store.subchainid
                            # Add more store attributes here if needed
                        }
                        subchain_data['stores'].append(store_data)
                        subchain_exists = True
                        break

                if not subchain_exists:
                    # If the subchain does not exist, create a new subchain entry
                    subchain_data = {
                        'sub_chain_id': store.subchainid,
                        'sub_chain_name': store.subchainname,
                        'stores': []
                    }
                    store_data = {
                        'store_id': store.storeid,
                        'store_name': store.storename,
                        'address': store.address,
                        'zipcode': store.zipcode,
                        'sub_chain_id': store.subchainid
                        # Add more store attributes here if needed
                    }
                    subchain_data['stores'].append(store_data)
                    chain_data['subchains'].append(subchain_data)

                chain_exists = True
                break

        if not chain_exists:
            # If the chain does not exist, create a new chain entry
            chain_data = {
                'chain_id': store.chain_id,
                'chain_name': store.chainname,
                'subchains': []
            }
            subchain_data = {
                'sub_chain_id': store.subchainid,
                'sub_chain_name': store.subchainname,
                'stores': []
            }
            store_data = {
                'store_id': store.storeid,
                'store_name': store.storename,
                'address': store.address,
                'zipcode': store.zipcode,
                'sub_chain_id': store.subchainid
                # Add more store attributes here if needed
            }
            subchain_data['stores'].append(store_data)
            chain_data['subchains'].append(subchain_data)
            city_data['chains'].append(chain_data)

    return city_data
