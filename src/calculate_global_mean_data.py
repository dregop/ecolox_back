from datetime import datetime, timedelta
from itertools import groupby
import json
from math import trunc
import statistics
from threading import Thread

from flask import jsonify, make_response
from src.models.lineChartData import LineChartDataSchema, lineChartData
# from models.lineChartData import LineChartDataSchema, lineChartData

from src.models.model import Session
# from models.model import Session


def calculate_global_mean_data(current_user):
    print('Calculate global meand data')
    session = Session()
    all_datas = []
    mean_datas = []
    data_objects = session.query(lineChartData).where(lineChartData.userId != 0).all()
    data_user = session.query(lineChartData).filter_by(userId=current_user.id).first()
    if data_user is None:
        print('No data for this user, we break')
        return
    # transforming into JSON-serializable objects
    schema = LineChartDataSchema(many=True)
    data_objects = schema.dump(data_objects)
    data_user = LineChartDataSchema().dump(data_user)
    date_to_start = datetime.strptime(json.loads(data_user['data'])[0]['date'][:16], '%Y-%m-%dT%H:%M')

    date_to_stop = datetime.strptime(json.loads(data_user['data'])[len(json.loads(data_user['data'])) - 1]['date'][:16], '%Y-%m-%dT%H:%M')
    delta_co2_user = int(json.loads(data_user['data'])[0]['co2']) # to start from from the first value of the user

    for object in data_objects:
        if object['data']:
            all_datas.append(json.loads(object['data']))

    for data in all_datas:
        if len(data) > 0:
            delta_date = date_to_start - datetime.strptime(data[0]['date'][:16], '%Y-%m-%dT%H:%M') # gives a timedelta like -10 days
            delta_co2 = int(data[0]['co2']) # to start from from the first c02 value for each user
            i = 0
            for point in data[:]: # [:] to update data during for loop of itself
                if isinstance(point['date'], str):
                    point['date'] = datetime.strptime(point['date'][:16], '%Y-%m-%dT%H:%M')
                if point['date'] + delta_date > date_to_stop:
                    data.remove(point)
                else:
                    point['date'] = point['date'] + delta_date # we add the time delta
                    point['co2'] = int(point['co2']) - delta_co2 + delta_co2_user
                
                    if i < len(data) - 1:
                        if isinstance(data[i+1]['date'], str):
                            data[i+1]['date'] = datetime.strptime(data[i+1]['date'][:16], '%Y-%m-%dT%H:%M')
                        diff_between_sibblings = data[i+1]['date'] - point['date']
                        if diff_between_sibblings.total_seconds() == 0 and point in data:
                            data.remove(point)
                        elif abs(diff_between_sibblings.total_seconds()) >= 3600: # if diff superior to one hour, we add the previous value so that there is not missing values
                            nbreHoursToAdd = trunc(abs(diff_between_sibblings.total_seconds()) / 3600)
                            while nbreHoursToAdd > 0:
                                data.insert(i, {'date': point['date'] + timedelta(hours=nbreHoursToAdd), 'co2': point['co2']})
                                nbreHoursToAdd = nbreHoursToAdd - 1
                i+=1

    for data in all_datas:
        for k,v in groupby(data,key=lambda x: x['date'].strftime('%Y-%m-%dT%H')[:13] + ':00Z'): # we stringify the date and group by date
            mean_datas.append({'date': k, 'co2': statistics.mean([x['co2'] for x in list(v)])})

    mean_datas.sort(key=lambda r: r['date'])

    print(mean_datas[0])

    # closest datapoint pour la moyenne : car quand pas de point ça compte pour 0 alors que ça devrait pas

    data = dict()
    data['category'] = 'internet_global_mean'
    data['userId'] = current_user.id
    data['data'] = json.dumps(mean_datas)

    data = LineChartDataSchema().load(data)
    data = lineChartData(**data)

    if session.query(lineChartData).where(lineChartData.userId == current_user.id, lineChartData.category == 'internet_global_mean').first():
        session.query(lineChartData).where(lineChartData.userId == current_user.id, lineChartData.category == 'internet_global_mean').update({lineChartData.data: data.data, lineChartData.updated_at: datetime.now()})
    else:
        session.add(data)
    session.commit()
    session.close()   

def parseDate(dct):
    for k,v in dct.items():
        print(v)
        if isinstance(v, datetime):
            try:
                dct[k] = v + timedelta(hours=2)
            except:
                pass
    return dct

def start_bot(current_user):
    global bot_thread
    bot_thread = Thread(target=calculate_global_mean_data(current_user), daemon=True)
    bot_thread.start()

def stop_bot():
    if bot_thread:
        bot_thread.join()