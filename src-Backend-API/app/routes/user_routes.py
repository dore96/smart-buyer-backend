from flask import Blueprint, request
from app.services.user_service import createUser

user_api = Blueprint('user_api', __name__)

@user_api.route('/user', methods=['POST'])
def createUserRequestHandler():
    return createUser(request.json)