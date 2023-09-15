from flask import Blueprint,jsonify
from app.services.api_services import get_chains_ids , get_store_data_by_chain ,get_store_data_by_city


# Create a Flask Blueprint for the open API
open_api = Blueprint('open_api', __name__)

# Route to retrieve all chain IDs
@open_api.route('/store/chain', methods=['GET'])
def cart():
    """
    Retrieves a list of all chain IDs.

    Returns:
        JSON response containing a list of chain IDs.
    """
    return jsonify(get_chains_ids())

# Route to retrieve store data by a specific chain ID
@open_api.route('/store/chain/<chain_id>', methods=['GET'])
def get_store_by_chain(chain_id):
    """
    Retrieves store data for a specific chain stores information based on the provided chain ID.

    Args:
        chain_id (str): The unique identifier for the chain.

    Returns:
        JSON response containing store data for the specified chain.
    """
    store_data = get_store_data_by_chain(chain_id)
    return jsonify(store_data)

# Route to retrieve store data by a specific city name
@open_api.route('/store/city/<city_name>', methods=['GET'])
def get_store_by_city(city_name):
    """
    Retrieves store data for a specific city based on the provided city name.

    Args:
        city_name (str): The name of the city to filter store data.

    Returns:
        JSON response containing store data for the specified city.
    """
    store_data = get_store_data_by_city(city_name)
    return jsonify(store_data)
    