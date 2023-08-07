from flask import Blueprint

# Import individual route files
from .user_routes import user_api
from .cart_routes import cart_api
from .api_routs import open_api

# Register blueprints for each service
api_blueprints = [user_api, cart_api,open_api]
