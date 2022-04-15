from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, Flask, jsonify
import boto3
from moto import mock_dynamodb2
import models
import pandas as pd

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
    response = dynamodb.client.execute_statement(Statement="SELECT * FROM detected_objects where date>= begin_day and date<= end_day")
    data = response['Items']
    list_of_vehicles = []
    for lst in data:
        list_of_vehicles.append(from_dynamodb_to_json(lst))
    response_message = {
        "data": list_of_vehicles,
        "total_count": len(data)
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


@app.route('/findObjectsByFilter')
def find_objects_by_filter():  # put application's code here
    args = request.args
    begin_day = args.get("begin_day", default="", type=str)
    end_day = args.get("end_day", default="", type=str)
    begin_time = args.get("begin_time", default="", type=str)
    end_time = args.get("end_time", default="", type=str)
    startingPosition = args.get("startingPosition", default="", type=str)
    endingPosition = args.get("endingPosition", default="", type=str)
    return 'Received ' + begin_day + "," + end_day


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

if __name__ == '__main__':
    app.run()
