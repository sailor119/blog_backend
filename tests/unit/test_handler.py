import json
import pytest
from dynamodbPyOperator import app
from datetime import datetime, timezone

@pytest.fixture()
def apigw_event():
    """ Generates API GW GET Event"""
    now = datetime.now(tz=timezone.utc).strftime('%a, %b %d %y %H:%M:%S GMT')
    mockRequest = []
    for visitType in ['pv', 'uv']:
        for method in ['GET', 'PUT']:
            basicRequest = {
                "resource": "/{proxy+}",
                "routeKey": "{} ".format(method) + "/visitors/{visitType}",
                "requestContext": {
                    "resourceId": "123456",
                    "apiId": "1234567890",
                    "resourcePath": "/{proxy+}",
                    "httpMethod": "{}".format(method),
                    "requestId": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef",
                    "accountId": "123456789012",
                    "identity": {
                        "apiKey": "",
                        "userArn": "",
                        "cognitoAuthenticationType": "",
                        "caller": "",
                        "userAgent": "Custom User Agent String",
                        "user": "",
                        "cognitoIdentityPoolId": "",
                        "cognitoIdentityId": "",
                        "cognitoAuthenticationProvider": "",
                        "sourceIp": "127.0.0.1",
                        "accountId": "",
                    },
                    "stage": "prod",
                },
                "stage": "$default",
                "headers": {
                    "Via": "1.1 08f323deadbeefa7af34d5feb414ce27.cloudfront.net (CloudFront)",
                    "Accept-Language": "en-US,en;q=0.8",
                    "CloudFront-Is-Desktop-Viewer": "true",
                    "CloudFront-Is-SmartTV-Viewer": "false",
                    "CloudFront-Is-Mobile-Viewer": "false",
                    "X-Forwarded-For": "127.0.0.1, 127.0.0.2",
                    "CloudFront-Viewer-Country": "US",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Upgrade-Insecure-Requests": "1",
                    "X-Forwarded-Port": "443",
                    "Host": "1234567890.execute-api.us-east-1.amazonaws.com",
                    "X-Forwarded-Proto": "https",
                    "X-Amz-Cf-Id": "aaaaaaaaaae3VYQb9jd-nvCd-de396Uhbp027Y2JvkCPNLmGJHqlaA==",
                    "CloudFront-Is-Tablet-Viewer": "false",
                    "Cache-Control": "max-age=0",
                    "User-Agent": "Custom User Agent String",
                    "CloudFront-Forwarded-Proto": "https",
                    "Accept-Encoding": "gzip, deflate, sdch",
                },
                "pathParameters": {"visitType": visitType},
                "rawPath": "/visitors/{}".format(visitType),
            }
            if method == 'PUT':
                basicRequest['body'] = json.dumps({
                    'visitType': visitType,
                    'info': {
                        'num': 5,
                        'now': now
                    }
                })
            mockRequest.append(basicRequest)
    return mockRequest

def test_lambda_handler(apigw_event, mocker):
    mockRequest = apigw_event
    for request in mockRequest:
        ret = app.lambda_handler(request, "")
        print(ret)
        data = json.loads(ret["body"])

        assert ret["statusCode"] == 200
        if request['requestContext']['httpMethod'] == 'GET':
            assert "Item" in ret["body"]
            assert isinstance(data["Item"], dict)
        else:
            assert "Attributes" in ret["body"]
            assert isinstance(data["Attributes"], dict)