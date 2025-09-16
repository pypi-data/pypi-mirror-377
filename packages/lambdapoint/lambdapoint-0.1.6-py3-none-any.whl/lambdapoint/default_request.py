from __future__ import annotations

import requests
import json
from abc import ABC, abstractmethod
from urllib.parse import urljoin

from lambdapoint.lambda_helper.invoke_lambda import invoke_lambdas
from lambdapoint.lambda_helper.lambda_event_builder import LambdaEventBuilder
from lambdapoint.lambda_mapping import LambdaMapping
from lambdapoint.execution_type import ExecutionType

class DefaultRequest(ABC):
    base_url = None
    execution_type: ExecutionType = ExecutionType.API
    default_headers: dict = {}

    def set_base_url(self,base_url: str) -> DefaultRequest:
        self.base_url = base_url
        return self
    
    def set_execution_type(self, execution_type: ExecutionType) -> DefaultRequest:
        self.execution_type = execution_type
        return self
    
    def set_default_headers(self, default_headers: dict) -> DefaultRequest:
        self.default_headers = default_headers
        return self

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DefaultRequest, cls).__new__(cls)
        return cls.instance
        
    def post(
            self,
            endpoint: str,
            body: dict,
            query_params:dict = {},
            extra_headers: dict = {},
            use_default_headers = True,
            allow_redirects=True
        ) -> requests.Response:
        return self.default_request(
            'POST',
            endpoint,
            body,
            query_params,
            extra_headers,
            use_default_headers,
            allow_redirects
        )

    def put(
            self,
            endpoint: str,
            body: dict,
            query_params:dict = {},
            extra_headers: dict = {},
            use_default_headers = True,
            allow_redirects=True
        ) -> requests.Response:
        return self.default_request(
            'PUT',
            endpoint,
            body,
            query_params,
            extra_headers,
            use_default_headers,
            allow_redirects
        )
    
    def patch(
            self,
            endpoint: str,
            body: dict,
            query_params:dict = {},
            extra_headers: dict = {},
            use_default_headers = True,
            allow_redirects=True
        ) -> requests.Response:
        return self.default_request(
            'PATCH',
            endpoint,
            body,
            query_params,
            extra_headers,
            use_default_headers,
            allow_redirects
        )
        

    def get(self,
            endpoint: str,
            query_params:dict = {},
            extra_headers: dict = {},
            use_default_headers = True,
            allow_redirects=True
        ) -> requests.Response:
        return self.default_request(
            'GET',
            endpoint,
            None,
            query_params,
            extra_headers,
            use_default_headers,
            allow_redirects
        )

    def delete_req(
            self,
            endpoint: str,
            query_params:dict = {},
            extra_headers: dict = {},
            use_default_headers = True,
            allow_redirects=True
        ) -> requests.Response:
        return self.default_request(
            'DELETE',
            endpoint,
            None,
            query_params,
            extra_headers,
            use_default_headers,
            allow_redirects
        )

    def default_request(
            self,
            method: str,
            endpoint: str,
            body: dict,
            query_params:dict = {},
            extra_headers: dict = {},
            use_default_headers = True,
            allow_redirects=True) -> requests.Response:
        headers = self.default_headers if use_default_headers else {}
        complete_headers = headers | extra_headers
        url = urljoin(self.base_url,endpoint)
        if self.execution_type == ExecutionType.API:
            prepared_url = requests.PreparedRequest()
            prepared_url.prepare_url(url,query_params)
            if method == 'GET':
                response = requests.get(prepared_url.url,headers=complete_headers,allow_redirects=allow_redirects)
            if method == 'DELETE':
                response = requests.delete(prepared_url.url,headers=complete_headers,allow_redirects=allow_redirects)
            elif method == 'POST':
                response = requests.post(prepared_url.url,json=body,headers=complete_headers,allow_redirects=allow_redirects)
            elif method == 'PUT':
                response = requests.put(prepared_url.url,json=body,headers=complete_headers,allow_redirects=allow_redirects)
            elif method == 'PATCH':
                response = requests.patch(prepared_url.url,json=body,headers=complete_headers,allow_redirects=allow_redirects)
                
        else:
            function_name,path_parameters = self.get_lambda_name_by_endpoint(f'{endpoint}', method.upper())
            if not function_name: raise Exception(f'Invalid path {endpoint}')
            builder = LambdaEventBuilder(function_name)\
                        .add_path(endpoint)\
                        .add_headers(complete_headers)\
                        .add_http_method(method.upper())\
                        .add_query_parameters(query_params)\
                        .add_path_parameters(path_parameters)\
                        .add_body(body)
            lambda_response = invoke_lambdas(builder)
            response = self.lambda_response_to_response(lambda_response)
            prepared_url = None


        self.log_request(
            method.upper(),
            prepared_url.url if prepared_url else '',
            complete_headers,
            query_params,
            body,
            response
        )

        return response

        
    def lambda_response_to_response(lambda_response: dict) -> requests.Response:
        lambda_payload = json.loads(lambda_response['Payload'].read().decode('utf-8'))
        response = requests.Response()
        response.status_code = lambda_payload['statusCode']
        if 'content-type' in lambda_payload['headers']:
            lambda_payload['headers']['Content-Type'] = lambda_payload['headers']['content-type']

        response.headers = lambda_payload['headers']
        response._content = lambda_payload['body'].encode()

        return  response

    @abstractmethod
    def log_request(self,method: str, url: str,headers: dict, query_params: dict, body: dict, response: requests.Response):
        pass

    @abstractmethod
    def get_lambda_name_by_endpoint(self,path:str, method: str) -> LambdaMapping:
        pass