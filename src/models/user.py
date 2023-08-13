from sqlalchemy import Column, String
from marshmallow import Schema, fields
from .model import Model, Base


class User(Model, Base):
    __tablename__ = 'user'

    login = Column(String(50))
    password = Column(String(250))

    def __init__(self, login, password):
        Model.__init__(self)
        self.login = login
        self.password = password

        
class ExamSchema(Schema):
    id = fields.Number()
    login = fields.Str()
    password = fields.Str()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()