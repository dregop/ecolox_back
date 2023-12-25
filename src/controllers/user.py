from datetime import datetime, timedelta
from flask import Blueprint, flash, jsonify, make_response, redirect, request, url_for
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from jose import jwt
from src.calculate_global_mean_data import start_bot
from src.forgot_password import reset_password, reset_password_email_send
# from calculate_global_mean_data import start_bot
from src.models.lineChartData import LineChartDataSchema, lineChartData
# from models.lineChartData import LineChartDataSchema, lineChartData
from src.models.user import User, UserSchema
# from models.user import User, UserSchema
from src.models.model import Session
# from models.model import Session
from src.auth import AuthError, token_required
# from auth import AuthError, token_required


user = Blueprint('user', __name__)
@user.route('/line_chart_data/all')
@token_required
def get_global_data(current_user):
    # fetching from the database
    session = Session()
    data_objects = session.query(lineChartData).where(lineChartData.userId == current_user.id, lineChartData.category == 'internet_global_mean').first()

    # transforming into JSON-serializable objects
    data = LineChartDataSchema().dump(data_objects)

    # serializing as JSON
    session.close()
    return jsonify(data)


@user.route('/line_chart_data')
@token_required
def get_data(current_user):

    # fetching from the database
    session = Session()
    data = session.query(lineChartData).where(lineChartData.userId == current_user.id, lineChartData.category == 'internet').first()

    # transforming into JSON-serializable objects
    data = LineChartDataSchema().dump(data)

    # serializing as JSON
    session.close()
    return jsonify(data)


@user.route('/line_chart_data', methods=['POST'])
@token_required
def add_data(current_user):
    # mount lineChart object
    data = request.get_json()
    data['userId'] = current_user.id
    data = LineChartDataSchema().load(data)
    data = lineChartData(**data)
    
    session = Session()
    lineData = session.query(lineChartData).filter_by(userId=current_user.id, category='internet').first()
    if lineData:
        session.close()
        return  make_response('Erreur, des données sont déjà enregistrées pour ce compte', 200)


    session.add(data)
    session.commit()
    new_data = LineChartDataSchema().dump(data)
    session.close()
    return jsonify(new_data)


@user.route('/line_chart_data', methods=['PUT'])
@token_required
def update_data(current_user):
    try:
        # start daemon to calculate global mean
        start_bot(current_user)
    except Exception as err:
        print(err)
        return make_response(str(err), 200)

    # mount lineChart object
    data = request.get_json()
    data['userId'] = str(current_user.id)
    data = LineChartDataSchema().load(data)
    data = lineChartData(**data)

    # persist exam
    session = Session()
    session.query(lineChartData).where(lineChartData.userId == current_user.id, lineChartData.category == 'internet').update({lineChartData.data: data.data, lineChartData.updated_at: datetime.now()})
    session.commit()

    # return created exam
    updated_data = LineChartDataSchema().dump(data)
    session.close()
    return jsonify(updated_data), 201


@user.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

@user.route('/signup', methods=['POST'])
def signup_post():
    from src.main import app
    # from main import app

    data = request.get_json()
    email = data['email']
    login = data['login']
    password = data['password']

    session = Session()
    user = session.query(User).filter_by(email=email).first() # if this returns a user, then the user already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        # serializing as JSON
        session.close()
        return  make_response('L\'email existe déjà c\'est ballot !', 200)

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, login=login, password=generate_password_hash(password, method='scrypt'))

    # add the new user to the database
    session.add(new_user)

    session.commit()

    token = jwt.encode({'public_id': new_user.id, 'exp' : datetime.utcnow() + timedelta(minutes=130000)}, app.config['SECRET_KEY'])  
    return jsonify({'idToken' : token, 'expiresIn': datetime.utcnow() + timedelta(minutes=130000)})

@user.route('/login', methods=['POST'])
def login_post():
    from src.main import app
    # from main import app

    data = request.get_json()
    email = data['email']
    password = data['password']
    # remember = True if data['remember'] else False

    session = Session()
    user = session.query(User).filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        return  make_response('Tu ne te souviens plus de ton mot de passe ou quoi ?', 200)
    token = jwt.encode({'public_id': user.id, 'exp' : datetime.utcnow() + timedelta(minutes=130000)}, app.config['SECRET_KEY'])
    return jsonify({'idToken' : str(token), 'expiresIn': datetime.utcnow() + timedelta(minutes=130000)})

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

@user.route('/test', methods=['POST'])
def test():
    return jsonify({'test' : 'valid'}) 


@user.route('/forgot_password', methods=['POST'])
def forgot():
    """
    POST response method for forgot password email send user.
    :return: JSON object
    """
    input_data = request.get_json()
    return reset_password_email_send(input_data)


@user.route('/reset_password/<token>', methods=['POST'])
def reset(token):
    """
    POST response method for save new password.
    :return: JSON object
    """
    input_data = request.get_json()
    return reset_password(input_data, token)