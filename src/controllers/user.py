import datetime
from flask import Blueprint, flash, jsonify, make_response, redirect, request, url_for
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from jose import jwt
from src.models.lineChartData import LineChartDataSchema, lineChartData
from src.models.user import User, UserSchema
from ..models.model import Session, engine, Base
from ..auth import AuthError, get_token_auth_header, requires_auth, token_required


user = Blueprint('user', __name__)
@user.route('/line_chart_data')
def get_data():
    # fetching from the database
    session = Session()
    data_objects = session.query(lineChartData).all()

    # transforming into JSON-serializable objects
    schema = LineChartDataSchema(many=True)
    data = schema.dump(data_objects)

    # serializing as JSON
    session.close()
    return jsonify(data)


@user.route('/line_chart_data', methods=['POST'])
@token_required
def add_data(current_user):
    # mount lineChart object
    data = request.get_json()
    print(data)
    data['userId'] = str(current_user.id)
    print(data)
    data = LineChartDataSchema().load(data)
    data = lineChartData(**data, created_by="HTTP post request")

    # persist exam
    session = Session()
    session.add(data)
    session.commit()

    # return created exam
    new_data = LineChartDataSchema().dump(data)
    session.close()
    return jsonify(new_data), 201

@user.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

@user.route('/signup', methods=['POST'])
def signup_post():
    from src.main import app

    data = request.get_json()  
    login = data['login']
    password = data['password']

    session = Session()
    user = session.query(User).filter_by(login=login).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        # serializing as JSON
        session.close()
        return  make_response('User already exists', 200)

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(login=login, password=generate_password_hash(password, method='scrypt'))

    # add the new user to the database
    session.add(new_user)

    session.commit()

    token = jwt.encode({'public_id': new_user.id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])  
    return jsonify({'idToken' : token, 'expiresIn': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)})

@user.route('/login', methods=['POST'])
def login_post():
    from src.main import app

    data = request.get_json()
    login = data['login']
    password = data['password']
    # remember = True if data['remember'] else False

    session = Session()
    user = session.query(User).filter_by(login=login).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        return  make_response('incorrect password', 200)
    token = jwt.encode({'public_id': user.id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
    return jsonify({'idToken' : str(token), 'expiresIn': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)})

# @user.route('/login', methods=['GET', 'POST'])  
# def login_user(): 
#     from src.main import app
 
#     auth = request.authorization   

#     if not auth or not auth.username or not auth.password:  
#         return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})    

#     user = User.query.filter_by(name=auth.username).first()
     
#     if check_password_hash(user.password, auth.password):  
#         token = jwt.encode({'public_id': user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])  
#         return jsonify({'token' : token.decode('UTF-8')}) 

#     return make_response('could not verify',  401, {'WWW.Authentication': 'Basic realm: "login required"'})

@user.route('/get_profile', methods=['GET'])
@token_required # return the current user
def get_profile(current_user):
    # transforming into JSON-serializable objects
    current_user = UserSchema().dump(current_user)
    # serializing as JSON
    return jsonify(current_user)