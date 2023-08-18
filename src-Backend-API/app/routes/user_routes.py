from flask import Blueprint, request, jsonify
from app.services.user_service import createUser,authenticate_user, deleteUser
from flask_jwt_extended import jwt_required, get_jwt_identity

user_api = Blueprint('user_api', __name__)

@user_api.route('/user', methods=['POST'])
def createUserRequestHandler():
    return createUser(request.json)

@user_api.route('/user/login', methods=['POST'])
def userLoginHandler():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # Authenticate the user using the provided email and password
    jwt_token = authenticate_user(email, password)

    if jwt_token:
        return jsonify({'token': jwt_token}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@user_api.route('/user/logout', methods=['GET'])
@jwt_required() 
def userLogoutHandler():
    # Get the current user's identity from the JWT token
    current_user = get_jwt_identity()
    return jsonify(message="Logout successful", user=current_user), 200

@user_api.route('/user/verify-token', methods=['GET'])
@jwt_required()
def verify_token():
    current_user = get_jwt_identity()
    return jsonify({'isValid': True, 'user': current_user}), 200

@user_api.route('/user', methods=['DELETE'])
@jwt_required()  
def userDeleteHandler():
   # Get the current user's identity from the JWT token
    current_user_email = get_jwt_identity()

    data = request.json
    email_to_delete = data.get('email')
    if current_user_email != email_to_delete:
        return jsonify(error="Permission denied"), 403

    # Call the deleteUser function to delete the user with the specified email
    deleted_user = deleteUser(email_to_delete)
    if deleted_user:
        return jsonify(message="User deleted successfully"), 200
    else:
        return jsonify(error="User not found"), 404