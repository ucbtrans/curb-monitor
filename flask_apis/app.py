from boto3.dynamodb.conditions import Attr
from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, Flask, jsonify
import boto3
from moto import mock_dynamodb2
import models
import pandas as pd
import datetime as dt
import json

app = Flask(__name__)
import db_connect as dynamodb
from boto3.dynamodb.types import TypeDeserializer


def from_dynamodb_to_json(item):
    d = TypeDeserializer()
    return {k: d.deserialize(value=v) for k, v in item.items()}


@app.route('/detected_objects')
def find_detected_objects():
    begin_day = request.args["begin_day"]
    end_day = request.args["end_day"]
    #begin_time = request.args["begin_time"]
    #end_time = request.args["end_time"]
    #startingPosition = request.args["startingPosition"]
    #endingPosition = request.args["endingPosition"]
    table = dynamodb.resource.Table('detected_objects')
    response = table.scan(
        FilterExpression=Attr("time").between(begin_day, end_day)
    )
    data = response['Items']

    list_of_vehicles = []
    # for lst in data:
    #     list_of_vehicles.append(from_dynamodb_to_json(lst))

    response_message = {
        "data": data,
        "total_count": len(data)
    }
    return jsonify(response_message)

@app.route('/speed_data')
def find_speed_data():
    table = dynamodb.resource.Table('speed_data')
    begin_day = request.args["begin_day"]
    end_day = request.args["end_day"]
    begin_time = request.args["begin_time"]
    end_time = request.args["end_time"]

    # Convert timestamps
    begin_day =  dt.datetime.strptime(begin_day, "%m/%d/%Y")
    begin_time = dt.datetime.strptime(begin_time, "%H:%M:%S")
    begin_ts = dt.datetime.combine(begin_day, begin_time.time())
    begin_ts = begin_ts.isoformat() + "Z"

    end_day =  dt.datetime.strptime(end_day, "%m/%d/%Y")
    end_time = dt.datetime.strptime(end_time, "%H:%M:%S")
    end_ts = dt.datetime.combine(end_day, end_time.time())
    end_ts = end_ts.isoformat() + "Z"

    print(begin_ts)
    print(end_ts)

    response = table.scan(
        FilterExpression=Attr("start_ts").between(begin_ts, end_ts)
    )
    data = response['Items']
    print(type(data))

    ca_speed = 0
    bus_speed = 0
    shattuck_speed = 0

   # list_of_objects = json.loads(data)
    # for lst in data:
    #     print(jsonify(lst))
    #     list_of_objects.append(from_dynamodb_to_json(lst))

    if len(data) == 0:
        return jsonify({        
            "College Ave": ca_speed,
            "Bus Stops": bus_speed,
            "Shattuck": shattuck_speed,
            "Unit": "mph"})

    df = pd.DataFrame.from_records(data)
    grouped = df.groupby(['segment','start_ts'])['speed'].first().groupby(['segment']).mean()
    print(grouped)
    if 'College Ave' in grouped.index:
        ca_speed = grouped['College Ave']
    if 'Bus Stop' in grouped.index:
        bus_speed = grouped['Bus Stop']
    if 'Shattuck' in grouped.index:
        shattuck_speed = grouped['Shattuck']


    response_message = {
        "College Ave": ca_speed,
        "Bus Stops": bus_speed,
        "Shattuck": shattuck_speed,
        "Unit": "mph"
    }
    return jsonify(response_message)



@app.route('/get_all_objects')
def find_objects():
    table = dynamodb.resource.Table('detected_objects')
    response = dynamodb.client.execute_statement(Statement="SELECT * FROM detected_objects")
    data = response['Items']
    list_of_vehicles = []
    for lst in data:
        list_of_vehicles.append(from_dynamodb_to_json(lst))
    response_message = {
        "data": list_of_vehicles,
        "total_count": len(data)
    }

    return jsonify(response_message)


@app.route('/display_all_objects')
def find_objects_1():
    table = dynamodb.resource.Table('detected_objects')
    response = dynamodb.client.execute_statement(Statement="SELECT * FROM detected_objects")
    data = response['Items']
    list_of_vehicles = []
    for lst in data:
        list_of_vehicles.append(from_dynamodb_to_json(lst))
    return render_template('all_vehicles.html', title='', vehicles=list_of_vehicles)


@app.route('/number_of_detections')
def number_of_detections():
    table = dynamodb.resource.Table('detected_objects')
    response = dynamodb.client.execute_statement(Statement="SELECT * FROM detected_objects")
    data = response['Items']
    list_of_objects = []
    for lst in data:
        list_of_objects.append(from_dynamodb_to_json(lst))
    df = pd.DataFrame(list_of_objects)
    total_count = df['obj_class_name'].value_counts()
    response_message = total_count.to_json()
    return jsonify(response_message)

@app.route('/video')
def generate_video_url():
    video_filename = request.args["video_filename"]
    name_of_file = 'all_videos_1/'+video_filename
    s3_client = boto3.client('s3')
    url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': 'curbside-data', 'Key': name_of_file},
        ExpiresIn=3600)

    response_message = {
        'name_of_file' : name_of_file,
        'url' : url
    }

    return jsonify(response_message)

if __name__ == '__main__':
    app.run()