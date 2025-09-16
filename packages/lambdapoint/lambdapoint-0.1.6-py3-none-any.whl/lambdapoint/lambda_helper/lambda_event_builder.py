from __future__ import annotations

import jwt
import json


class LambdaEventBuilder:
    function_name: str = ''
    path: str = ''
    http_method: str = ''
    headers: dict = {}
    query_parameters: dict = {}
    path_parameters: dict = {}
    body: dict = {}

    def __init__(self,function_name:str) -> None:
        self.function_name = function_name

    def add_path(self,path:str) -> LambdaEventBuilder:
        if path: self.path = path
        return self

    def add_http_method(self,http_method:str) -> LambdaEventBuilder:
        if http_method: self.http_method = http_method
        return self

    def add_headers(self,headers:dict) -> LambdaEventBuilder:
        if headers: self.headers = headers
        return self

    def add_query_parameters(self,query_parameters:dict) -> LambdaEventBuilder:
        if query_parameters: self.query_parameters = query_parameters
        return self

    def add_path_parameters(self,path_parameters:dict) -> LambdaEventBuilder:
        if path_parameters: self.path_parameters = path_parameters
        return self

    def add_body(self,body:dict) -> LambdaEventBuilder:
        if body: self.body = body
        return self
    
    def build(self) -> dict:
        if not self.http_method: raise Exception('No HHTP method was provided')
        if not self.path: raise Exception('No path was provided')
        if not self.function_name: raise Exception('No function name was provided')
        
        event = {
            "execute": "function",
            "function_name": self.function_name,
            "resource": "/",
            "path": self.path,
            "httpMethod": self.http_method,
            "requestContext": {
                "resourcePath": "/",
                "httpMethod": self.http_method,
                "path": self.path,

            },
        }

        if self.headers: 
            event['headers'] = self.headers
        if self.query_parameters:
            event['queryStringParameters'] = self.query_parameters
        if self.path_parameters:  
            event['pathParameters'] = self.path_parameters
        if self.body:
            event['body'] = json.dumps(self.body)

        if self.headers and 'Authorization' in self.headers:
            token_header = self.headers['Authorization']
            token = token_header.split(" ")[-1]
            token_decoded = jwt.decode(token, options={"verify_signature": False})
            event["requestContext"]["authorizer"] = {
                "lambda": token_decoded
            }

        return event




    

    