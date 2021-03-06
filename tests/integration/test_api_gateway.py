import os
from unittest import TestCase

import boto3
import requests
import simplejson as json
from datetime import datetime, timezone

"""
Make sure env variable AWS_SAM_STACK_NAME exists with the name of the stack we are going to test. 
"""


class TestApiGateway(TestCase):
    api_endpoint: str

    @classmethod
    def get_stack_name(cls) -> str:
        stack_name = os.environ.get("AWS_SAM_STACK_NAME")
        if not stack_name:
            raise Exception(
                "Cannot find env var AWS_SAM_STACK_NAME. \n"
                "Please setup this environment variable with the stack name where we are running integration tests."
            )

        return stack_name

    def setUp(self) -> None:
        """
        Based on the provided env variable AWS_SAM_STACK_NAME,
        here we use cloudformation API to find out what the HelloWorldApi URL is
        """
        stack_name = TestApiGateway.get_stack_name()

        client = boto3.client("cloudformation", region_name='us-east-1')

        try:
            response = client.describe_stacks(StackName=stack_name)
        except Exception as e:
            raise Exception(
                f"Cannot find stack {stack_name}. \n" f'Please make sure stack with the name "{stack_name}" exists.'
            ) from e

        stacks = response["Stacks"]

        stack_outputs = stacks[0]["Outputs"]
        api_outputs = [output for output in stack_outputs if output["OutputKey"] == "visitorApi2"]
        self.assertTrue(api_outputs, f"Cannot find output visitorApi2 in stack {stack_name}")

        self.api_endpoint = api_outputs[0]["OutputValue"]

    def test_api_gateway(self):
        """
        Call the API Gateway endpoint and check the response
        """
        for visitType in ['pv', 'uv']:
            now = datetime.now(tz=timezone.utc).strftime('%a, %b %d %y %H:%M:%S GMT')
            response = requests.get(self.api_endpoint.format(visitType=visitType))
            print(response.json())
            self.assertIsInstance(response.json(), dict)
            self.assertIn('Item', response.json().keys())
            data = {
                'visitType': visitType,
                'info': {
                    'now': now
                }
            }
            response = requests.put(self.api_endpoint.format(visitType=visitType), json=data)
            self.assertIsInstance(response.json(), dict)
            self.assertIn('Attributes', response.json().keys())
