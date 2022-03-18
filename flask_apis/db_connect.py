# import boto3
from boto3 import client, resource

AWS_ACCESS_KEY_ID=''
AWS_SECRET_ACCESS_KEY=''
REGION_NAME=''
# AWS_SESSION_TOKEN     = config("AWS_SESSION_TOKEN")

client = client(
    'dynamodb',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=REGION_NAME,
    # aws_session_token     = AWS_SESSION_TOKEN,
)

resource = resource(
    'dynamodb',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=REGION_NAME,
    # aws_session_token     = AWS_SESSION_TOKEN,
)