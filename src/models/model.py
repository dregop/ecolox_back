from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

db_url = 'localhost:3306'
db_name = 'nbgxjuuw_online-exam'
# db_user = 'nbgxjuuw_postgres'
# db_password = '0NLIN3-ex4m'
db_user = 'root'
db_password = ''
engine = create_engine(f'mysql+pymysql://{db_user}:{db_password}@{db_url}/{db_name}', pool_size=20, max_overflow=0)

# db_url = 'localhost:5432'
# db_name = 'online-exam'
# db_user = 'postgres'
# db_password = '0NLIN3-ex4m'
# engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_url}/{db_name}', pool_size=20, max_overflow=0)

Session = sessionmaker(bind=engine)
Base = declarative_base()


class Model():
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __init__(self):
        self.created_at = datetime.now()
        self.updated_at = datetime.now()