import boto3
import simplejson as json
from botocore.exceptions import ClientError
from botocore.config import Config

def init_item(table, visitType):
    visitTypeMapItem = {
        'pv': {
            'visitType':'pv',
            'info': {
                'num': 1,
                'description': 'use to describe page view numbers',
                'lastUpdateTime': ''
            }
        },
        'uv': {
            'visitType':'uv',
            'info': {
                'num': 1,
                'description': 'use to describe page view numbers',
                'lastUpdateTime': ''
            }
        }
    }
    item = visitTypeMapItem[visitType]
    table.put_item(Item=item)
    return item

def update_item(table, visitType, lastUpdateTime):
    body = table.update_item(
        Key={
            'visitType': visitType
        },
        UpdateExpression="SET info.num = info.num + :r, info.lastUpdateTime = :p",
        ExpressionAttributeValues={
            ":r": 1,
            ":p": lastUpdateTime
        },
        ReturnValues='UPDATED_NEW'
    )
    return body

def lambda_handler(event, context):
    #TODO implement
    config = Config(
        region_name = 'us-east-1',
        signature_version = 'v4',
        retries = {
            'max_attempts': 5,
            'mode': 'standard'
        }
    )
    dynamo = boto3.resource('dynamodb', config=config)
    table = dynamo.Table('visitors')

    try:
        if event["routeKey"] == "GET /visitors/{visitType}":
            visitType = event["pathParameters"]["visitType"]
            body = table.get_item(Key={
                'visitType': visitType
            })
            if 'Item' not in body.keys():
                item = init_item(table, visitType)
                body['Item'] = item
            statusCode = 200
        elif event["routeKey"] == "PUT /visitors/{visitType}":
            visitType = event["pathParameters"]["visitType"]
            requestJSON = json.loads(event['body'])
            lastUpdateTime = requestJSON['info']['now']
            try:
                body = update_item(table, visitType, lastUpdateTime)
            except ClientError:
                init_item(table, visitType)
                body = update_item(table, visitType, lastUpdateTime)
            statusCode = 200
        else:
            statusCode = 400
            body = "Unsupport method"
    except Exception as e:
        statusCode = 400
        body = "Get visitor info failed, failed reason is {}".format(e)
    return {
        'statusCode': statusCode,
        'body': json.dumps(body, use_decimal=True)
    }
