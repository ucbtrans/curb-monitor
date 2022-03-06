from decimal import Decimal
import json
import boto3
import os
import uuid
import pandas as pd

TABLE_NAME="detected_objects"
CSV_PATH=r"../../notebooks/filtered_out.csv"
key_id = os.getenv('aws_access_key_id')
key = os.environ.get('aws_secret_access_key')



def load_detected_objects(objects, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', aws_access_key_id=key_id, aws_secret_access_key=key, region_name='us-west-1')

    table = dynamodb.Table(TABLE_NAME)
    for object in objects:
        object['id'] = str(uuid.uuid1())
        table.put_item(Item=object)


if __name__ == '__main__':
    
    csv_file = pd.DataFrame(pd.read_csv(CSV_PATH, sep = ",", header = 0, index_col = False))
    csv_file.to_json(r'object_detected.json', orient = "records", date_format = "epoch", double_precision = 10, force_ascii = True, date_unit = "ms", default_handler = None)

    with open("object_detected.json") as json_file:
        object_list = json.load(json_file, parse_float=Decimal)
    load_detected_objects(object_list)