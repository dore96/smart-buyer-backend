from flask import Blueprint, request, jsonify
from app.services.user_service import create_user,authenticate_user, delete_user
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token

# Create a Flask Blueprint for the user API
user_api = Blueprint('user_api', __name__)

# Route to create a new user
@user_api.route('/user', methods=['POST'])
def createUserRequestHandler():
    """
    Endpoint for creating a new user.

    - POST: Create a new user based on the provided user data.

    Returns:
        JSON response containing the user creation result.
    """
    return create_user(request.json)


# Route to handle user login
@user_api.route('/user/login', methods=['POST'])
def userLoginHandler():
    """
    Endpoint for user login.

    - POST: Authenticate the user using the provided email and password and return a JWT token upon successful authentication.

    Returns:
        JSON response containing a JWT token or an error message.
    """
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # Authenticate the user using the provided email and password
    jwt_token = authenticate_user(email, password)

    if jwt_token:
        return jsonify({'token': jwt_token}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

# Route to handle user logout
@user_api.route('/user/logout', methods=['GET'])
@jwt_required() 
def userLogoutHandler():
    """
    Endpoint for user logout.

    - GET: Log the user out and return a successful logout message.

    Returns:
        JSON response indicating a successful logout.
    """
    # Get the current user's identity from the JWT token
    current_user = get_jwt_identity()
    return jsonify(message="Logout successful", user=current_user), 200


# Route to refresh a user's JWT token
@user_api.route('/user/refresh-token', methods=['GET'])
@jwt_required()
def refresh_token():
    """
    Endpoint to refresh a user's JWT token.

    - GET: Generate a new access token for the current user.

    Returns:
        JSON response containing a new JWT token.
    """
    current_user = get_jwt_identity()

    # Generate a new access token for the current user
    new_token = create_access_token(identity=current_user)

    return jsonify({'token': new_token}), 200


# Route to delete a user
@user_api.route('/user', methods=['DELETE'])
@jwt_required()  
def userDeleteHandler():
    """
    Endpoint for deleting a user.

    - DELETE: Delete the user with the specified email.

    Returns:
        JSON response indicating the result of the user deletion.
    """
   # Get the current user's identity from the JWT token
    current_user_email = get_jwt_identity()

    data = request.json
    email_to_delete = data.get('email')
    if current_user_email != email_to_delete:
        return jsonify(error="Permission denied"), 403

    # Call the deleteUser function to delete the user with the specified email
    deleted_user = delete_user(email_to_delete)
    if deleted_user:
        return jsonify(message="User deleted successfully"), 200
    else:
        return jsonify(error="User not found"), 404