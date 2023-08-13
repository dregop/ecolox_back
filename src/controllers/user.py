import datetime
from flask import Blueprint, flash, jsonify, make_response, redirect, request, url_for
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from jose import jwt
from src.models.lineChartData import LineChartDataSchema, lineChartData
from src.models.user import User
from ..models.model import Session, engine, Base
from ..auth import AuthError, requires_auth, token_required


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
def add_data():
    # mount lineChart object
    data = LineChartDataSchema().load(request.get_json())
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
    print('hello')
    data = request.get_json()  
    login = data['login']
    password = data['password']

    session = Session()
    user = session.query(User).filter_by(login=login).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        return someting

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(login=login, password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    session.add(new_user)
    session.commit()

    return something

@user.route('/login', methods=['POST'])
def login_post():
    from src.main import app
    login = request.form.get('login')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(login=login).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return  something # if the user doesn't exist or password is wrong, reload the page
    
    token = jwt.encode({'public_id': user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])  
    return jsonify({'token' : token.decode('UTF-8')}) 

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