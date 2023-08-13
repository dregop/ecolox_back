from sqlalchemy import Column, String
from marshmallow import Schema, fields
from .model import Model, Base


class lineChartData(Model, Base):
    __tablename__ = 'line_chart_data'

    userId = Column(String)
    category = Column(String)
    data = Column(String)

    def __init__(self, userId, category, data, created_by):
        Model.__init__(self, created_by)
        self.userId = userId
        self.category = category
        self.data = data

        
class LineChartDataSchema(Schema):
    id = fields.Number()
    userId = fields.Str()
    category = fields.Str()
    data = fields.Str()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    last_updated_by = fields.Str()