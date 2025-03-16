# user/jwt_utils.py
import jwt
from datetime import datetime, timedelta
from django.conf import settings

# Secret key for signing the JWT tokens (you should store this in settings)
SECRET_KEY = 'your-secret-key'  # Replace with a secure key in production

def create_jwt_token(user_id, role):
    """
    Create a JWT token for the given user ID and role.
    """
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(days=1)  # Token expires in 1 day
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

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