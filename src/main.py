from flask import Flask, jsonify, request
from flask_cors import CORS

from src.controllers.user import user
from .models.model import Session, engine, Base
from .models.exam import Exam, ExamSchema
from .auth import AuthError, requires_auth

# creating the Flask application
app = Flask(__name__)
CORS(app) # TODO need probably to deel with more restriction in the future
app.config['SECRET_KEY'] = 'secret-key-goes-here'

# if needed, generate database schema
Base.metadata.create_all(engine)

# import routes
app.register_blueprint(user)

@app.route('/exams')
def get_exams():
    # fetching from the database
    session = Session()
    exam_objects = session.query(Exam).all()

    # transforming into JSON-serializable objects
    schema = ExamSchema(many=True)
    exams = schema.dump(exam_objects)

    # serializing as JSON
    session.close()
    return jsonify(exams)


@app.route('/exams', methods=['POST'])
def add_exam():
    # mount exam object
    posted_exam = ExamSchema(only=('title', 'description')).load(request.get_json())
    exam = Exam(**posted_exam, created_by="HTTP post request")

    # persist exam
    session = Session()
    session.add(exam)
    session.commit()

    # return created exam
    new_exam = ExamSchema().dump(exam)
    session.close()
    return jsonify(new_exam), 201

@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response