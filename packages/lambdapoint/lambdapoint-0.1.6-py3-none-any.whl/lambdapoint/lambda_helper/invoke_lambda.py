import boto3
import json

from lambdapoint.lambda_helper.lambda_event_builder import LambdaEventBuilder

def invoke_lambdas(event_builder: LambdaEventBuilder):
    client = boto3.client('lambda','us-east-1')
    return client.invoke(
        FunctionName=event_builder.function_name,
        Payload=json.dumps(event_builder.build())
    )

def get_latest_version(function_name: str) -> str:
    client = boto3.client('lambda','us-east-1')
    response = client.list_versions_by_function(FunctionName=function_name)
    versions = response['Versions']
    latest_version = versions[-1]
    return latest_version['Version']