from flask import Flask, jsonify, request
from flask_cors import CORS

from src.controllers.user import user
from .models.model import Session, engine, Base
from .auth import AuthError, requires_auth

# creating the Flask application
app = Flask(__name__)
CORS(app) # TODO need probably to deel with more restriction in the future
app.config['SECRET_KEY'] = 'secret-key-goes-here'

# if needed, generate database schema
Base.metadata.create_all(engine)

# import routes
app.register_blueprint(user)

@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response