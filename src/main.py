# import subprocess
from flask import Flask, jsonify
from flask_cors import CORS

from src.controllers.user import user
# from controllers.user import user
from src.models.model import engine, Base
# from models.model import engine, Base
from src.auth import AuthError
# from auth import AuthError

from flask_mail import Mail
mail = Mail()

# execute the shell script
# subprocess.call(['sh', '../bootstrap.sh'])

# creating the Flask application
app = Flask(__name__)
mail = Mail(app)

# This is the configuration for the email server.
app.config["MAIL_SERVER"] = "node10-fr.n0c.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = "nepasrepondre@ecobuddy.fr"
app.config["MAIL_PASSWORD"] = 'PZDj9cEvdrQG5Ja'
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True

mail = Mail(app)

# if __name__ == '__main__':
#     app.run()

CORS(app) # TODO: need probably to deel with more restriction in the future
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