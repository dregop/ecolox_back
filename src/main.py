# import subprocess
from flask import Flask, jsonify
from flask_cors import CORS

from src.controllers.user import user
# from controllers.user import user
from src.models.model import engine, Base
# from models.model import engine, Base
from src.auth import AuthError
# from auth import AuthError

# execute the shell script
# subprocess.call(['sh', '../bootstrap.sh'])

# creating the Flask application
app = Flask(__name__)

# if __name__ == '__main__':
#     app.run()

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