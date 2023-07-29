from flask import Flask
from .models import db
from .routes import api_blueprints
from flask_cors import CORS 

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    db.init_app(app)

    # Enable CORS for all routes
    CORS(app)   

    # Register all the blueprints from the `api_blueprints` list
    for blueprint in api_blueprints:
        app.register_blueprint(blueprint)

    return app