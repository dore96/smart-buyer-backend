import bcrypt
import jwt
from datetime import datetime, timedelta
from app.models import User, db
import os
import re

def format_user(user):
    return {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "created_at": user.created_at
    }

def createUser(data):
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    password = data.get('password')

    # Check if a user email is a valid email
    if not re.match(r'^[a-zA-Z0-9.!#$%&*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$', email):
        return {'error': 'Invalid email'}, 400

    # Check if a user with the same email already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return {'error': 'User with this email already exists'}, 409

    user = User(first_name=first_name, last_name=last_name, email=email, password=password)
    db.session.add(user)
    db.session.commit()
    return format_user(user)

def authenticate_user(email, password):

    # Get the user from the database by email
    user = User.query.filter_by(email=email).first()

    # Check if the user exists and the password is correct
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        # Generate the JWT token with the user's email as the payload
        token_payload = {
            'sub': user.email,
            'exp': datetime.utcnow() + timedelta(days=1)
        }

        # Encode the payload and create the JWT token
        jwt_token = jwt.encode(token_payload, 'dorIsTheKingdrtfsgyuhdji', algorithm='HS256')

        return jwt_token

    return None

def deleteUser(user_email):
    # Check if the user with the given user_id exists in the database
    user = User.query.filter_by(email=user_email).first()
    if not user:
        return False  # User not found, return False

    try:
        # Delete the user from the database
        db.session.delete(user)
        db.session.commit()
        return True  
    except:
        db.session.rollback()
        return False  