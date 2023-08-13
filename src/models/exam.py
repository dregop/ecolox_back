from sqlalchemy import Column, String
from marshmallow import Schema, fields
from .model import Model, Base


class Exam(Model, Base):
    __tablename__ = 'exams'

    title = Column(String)
    description = Column(String)

    def __init__(self, title, description, created_by):
        Model.__init__(self, created_by)
        self.title = title
        self.description = description

        
class ExamSchema(Schema):
    id = fields.Number()
    title = fields.Str()
    description = fields.Str()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    last_updated_by = fields.Str()