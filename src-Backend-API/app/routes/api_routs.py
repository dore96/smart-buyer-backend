from flask import Blueprint,jsonify
from app.services.api_services import get_chains_ids , get_store_data_by_chain ,get_store_data_by_city

open_api = Blueprint('open_api', __name__)

@open_api.route('/store/chain', methods=['GET'])
def cart():
    return jsonify(get_chains_ids())

@open_api.route('/store/chain/<chain_id>', methods=['GET'])
def get_store_by_chain(chain_id):
    store_data = get_store_data_by_chain(chain_id)
    return jsonify(store_data)

@open_api.route('/store/city/<city_name>', methods=['GET'])
def get_store_by_city(city_name):
    store_data = get_store_data_by_city(city_name)
    return jsonify(store_data)
    