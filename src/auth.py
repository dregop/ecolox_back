from flask import jsonify, request
from functools import wraps
from jose import jwt
from urllib.request import urlopen
from src.models.model import Session
# from models.model import Session
from src.models.user import User
# from models.user import User


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    parts = auth.split()

    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    token = parts[1]
    return token


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        from src.main import app
        # from main import app
        token = get_token_auth_header()
        if not token:
            return jsonify({'message': 'a valid token is missing'})
        data = jwt.decode(token, app.config['SECRET_KEY'])
        session = Session()
        current_user = session.query(User).filter_by(id=data['public_id']).first()
        return f(current_user, *args, **kwargs)
    return decorator

