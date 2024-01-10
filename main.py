from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from flask import Flask, jsonify,request
from bson.json_util import dumps
import math
import os

app = Flask(__name__)

connection_string = r'mongodb://aromongo:%40r0dek%40412@mongodb.arodek.com:27017/?authMechanism=DEFAULT'
database_name = r'Cogniquest'
collection_name_ica=r'Ica_Test'
result_=r'Result_ica'

# Connect to MongoDB
client = MongoClient(connection_string)
db = client[database_name]
collection_ica = db[collection_name_ica]
collection_result = db[result_]


def ica_test(answer_new):
    value = [string.lower() for string in answer_new]
    text = ["animal", "non-animal"]
    count1 = 0
    count2 = 0
    count3 = 0
    total_animal_count=5
    for i in value:
        if i in text[0]:
            count1 += 1
        elif i in text[1]:
            count2 += 1
        else:
            count3=count3
    accuracy=(count1/total_animal_count)*100
    return accuracy

def Ica_score(user_id,test_id):
    try:
        test_id=ObjectId(test_id)
        user_report={ 
        'user_id':ObjectId(user_id),
        'test_id':ObjectId(test_id),
        'age':0,
        'MOCA_Score':0,
        'Accuracy':0,
        'Speed':0,
        'ICA_Index':0,
        'timestamp':datetime.now().strftime("%Y-%m-%d %H")
        }
        try:
            test_data = collection_ica.find_one({'_id':test_id})['testData']
            test_time = collection_ica.find_one({'_id':test_id})['testTime']
            speed_ica_text = round(min(100, 100 * (1 / math.exp((int(str(test_time).split('.')[0]) * 60 + int(str(test_time).split('.')[1])) / 1025))), 2)
            user_report['Speed']=speed_ica_text
            user_report['Accuracy']=ica_test(test_data)
            user_report['ICA_Index']=round((((user_report['Speed'])/100*(user_report['Accuracy'])/100)*100),2)
            collection_result.insert_one(user_report)
            return dumps(user_report)
        except Exception as e:
            user_report['Speed']=0
            user_report['Accuracy']=0
            user_report['ICA_Index']=0
            return dumps(user_report)
    except Exception as e:
        return dumps({"error": 'data_missing'})


@app.route('/result/<string:user_id>/<string:test_id>', methods=['GET'])
def get_result_by_test_id(user_id,test_id):
    list_inputs =[user_id,test_id]
    if user_id and test_id not in list_inputs:
        return jsonify({'error': '404 User not found'})
    else:
        try:
            return Ica_score(user_id,test_id)
        except TypeError as e:
            return jsonify({"error": 'data_missing'})
        except KeyError :
            return jsonify({"error": 'key_error'})


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
