from sqlalchemy import Column, String
from marshmallow import Schema, fields
from .model import Model, Base


class User(Model, Base):
    __tablename__ = 'user_app'

    email = Column(String(50))
    login = Column(String(50))
    password = Column(String(250))

    def __init__(self, email, login, password):
        Model.__init__(self)
        self.email = email
        self.login = login
        self.password = password

        
class UserSchema(Schema):
    id = fields.Number()
    email = fields.Str()
    login = fields.Str()
    password = fields.Str()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()