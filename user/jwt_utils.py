import os
import jwt
from datetime import datetime, timedelta
from django.conf import settings

# Get secret key from environment variables or Django settings
SECRET_KEY = os.getenv('SECRET_KEY', settings.SECRET_KEY)

def create_jwt_tokens(user_id, role):
    """
    Create access and refresh tokens for the given user ID and role.
    """
    access_token_payload = {
        'id': user_id,  # Standardizing to 'id' (matches your views)
        'role': role,
        'exp': datetime.utcnow() + timedelta(minutes=15)  # Expires in 15 minutes
    }
    access_token = jwt.encode(access_token_payload, SECRET_KEY, algorithm='HS256')

    refresh_token_payload = {
        'id': user_id,  # Standardizing to 'id'
        'exp': datetime.utcnow() + timedelta(days=7)  # Expires in 7 days
    }
    refresh_token = jwt.encode(refresh_token_payload, SECRET_KEY, algorithm='HS256')

    return access_token, refresh_token

def decode_jwt_token(token):
    """
    Decode a JWT token and return the payload.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return {"error": "Token has expired"}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}
