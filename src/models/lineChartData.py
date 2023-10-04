from sqlalchemy import Column, String, Numeric
from marshmallow import Schema, fields
from .model import Model, Base


class lineChartData(Model, Base):
    __tablename__ = 'line_chart_data'

    userId = Column(Numeric)
    category = Column(String)
    data = Column(String)

    def __init__(self, userId, category, data):
        Model.__init__(self)
        self.userId = userId
        self.category = category
        self.data = data

        
class LineChartDataSchema(Schema):
    id = fields.Number()
    userId = fields.Number()
    category = fields.Str()
    data = fields.Str()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    last_updated_by = fields.Str()