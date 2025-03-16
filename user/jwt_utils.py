# user/jwt_utils.py
import os
import jwt
from datetime import datetime, timedelta
from django.conf import settings

# Secret key for signing JWT tokens (replace with a secure key in production)
# SECRET_KEY = 'your-secret-key'
SECRET_KEY=os.getenv('SECRET_KEY')

def create_jwt_tokens(user_id, role):
    """
    Create access and refresh tokens for the given user ID and role.
    """
    # Access token payload (expires in 15 minutes)
    access_token_payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(minutes=15)  # Short-lived
    }
    access_token = jwt.encode(access_token_payload, SECRET_KEY, algorithm='HS256')

    # Refresh token payload (expires in 7 days)
    refresh_token_payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7)  # Long-lived
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
        return None  # Token has expired
    except jwt.InvalidTokenError:
        return None  # Invalid token