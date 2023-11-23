import datetime
from itertools import groupby
import json
import statistics
from threading import Thread

from flask import jsonify
from src.models.lineChartData import LineChartDataSchema, lineChartData
# from models.lineChartData import LineChartDataSchema, lineChartData

from src.models.model import Session
# from models.model import Session


def calculate_global_mean_data():
    session = Session()
    all_datas = []
    mean_datas = []
    data_objects = session.query(lineChartData).where(lineChartData.userId != 0).all()
    # transforming into JSON-serializable objects
    schema = LineChartDataSchema(many=True)
    data_objects = schema.dump(data_objects)
    for object in data_objects:
        if object['data']:
            all_datas.append(json.loads(object['data']))
    
    for data in all_datas:
        for k,v in groupby(data,key=lambda x:x['date'][:16] + 'Z'):
            mean_datas.append({'date': k, 'co2': statistics.mean([x['co2'] for x in list(v)])})

    mean_datas.sort(key=lambda r: r['date'])
    data = dict()
    data['category'] = 'internet'
    data['userId'] = 0 # 0 count for the mean global data of all users
    data['data'] = json.dumps(mean_datas)

    data = LineChartDataSchema().load(data)
    data = lineChartData(**data)

    if session.query(lineChartData).where(lineChartData.userId == 0).first():
        session.query(lineChartData).where(lineChartData.userId == 0).update({lineChartData.data: data.data, lineChartData.updated_at: datetime.datetime.now()})
    else:
        session.add(data)
    session.commit()
    session.close()   

def parseDate(dct):
    for k,v in dct.items():
        print(v)
        if isinstance(v, datetime):
            try:
                dct[k] = v + datetime.timedelta(hours=2)
            except:
                pass
    return dct       



def start_bot():
    global bot_thread
    bot_thread = Thread(target=calculate_global_mean_data, daemon=True)
    bot_thread.start()
    return

def stop_bot():
    if bot_thread:
        bot_thread.join()