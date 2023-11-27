from src.models.model import Session
from datetime import datetime, timedelta
from flask import jsonify, make_response
from flask_mail import Message
from jose import jwt
from werkzeug.security import generate_password_hash

from src.models.user import CreateResetPasswordEmailSendInputSchema, ResetPasswordInputSchema, User

def send_forgot_password_email(request, user):
    """
    It sends an email to the user with a link to reset their password
    :param request: The request object
    :param user: The user object of the user who requested the password reset
    """
    from src.main import app, mail

    mail_subject = "Eco Buddy: changement de mot de passe"
    domain = "localhost:4200/#"
    uid = user.id
    token = jwt.encode({'public_id': uid, 'exp' : datetime.utcnow() + timedelta(minutes=30)}, app.config['SECRET_KEY'])
    msg = Message(
        mail_subject, sender=app.config["MAIL_USERNAME"], recipients=[user.email]
    )
    msg.html = f"Bonjour, <br> Vous avez fait la demande pour changer votre mot de passe, cliquez sur le lien pour le changer : {domain}/mot-de-passe-oublie/{token}"
    msg.html += "<br><br> Si vous n'êtez pas à l'origine de cette demande, ne cliquez pas."
    msg.html += "Ceci est une messagerie automatique, ne pas répondre s'il vous plait."
    mail.send(msg)

def reset_password_email_send(request, input_data):
    """
    It takes an email address as input, checks if the email address is registered in the database, and
    if it is, sends a password reset email to that address
    :param request: The request object
    :param input_data: The data that is passed to the function
    :return: A response object with a message and status code.
    """
    create_validation_schema = CreateResetPasswordEmailSendInputSchema()
    errors = create_validation_schema.validate(input_data)
    if errors:
        return make_response(message=errors)
    session = Session()
    user = session.query(User).filter_by(email=input_data.get("email")).first()
    if user is None:
        return make_response("Aucun compte n'existe avec cet email. Es-tu vraiment sûr de toi ?", 200)
    send_forgot_password_email(request, user)
    return jsonify("Un lien "), 200

def reset_password(request, input_data, token):
    from src.main import app
    create_validation_schema = ResetPasswordInputSchema()
    errors = create_validation_schema.validate(input_data)
    if errors:
        return make_response(errors, 200)
    if not token:
        return make_response("Le token est manquant",200)
    token = jwt.decode(token, app.config['SECRET_KEY'])
    session = Session()
    user = session.query(User).filter_by(id=token.get('public_id')).first()
    if user is None:
        return make_response("Aucun compte n'existe avec cet email. Es-tu vraiment sûr de toi ?",200)
    print(user)
    password = generate_password_hash(input_data.get('password'), method='scrypt')
    session.query(User).where(User.id == token.get('public_id')).update({User.password: password, User.updated_at: datetime.now()})
    session.commit()
    return jsonify("New password SuccessFully set."), 200