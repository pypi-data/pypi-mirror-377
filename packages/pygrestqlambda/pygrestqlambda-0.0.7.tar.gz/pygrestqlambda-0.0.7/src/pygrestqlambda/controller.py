"""
Controller module to handle AWS API Gateway REST API proxy lambda integration
"""

from pygrestqlambda.aws.lambda_function.rest_api_gateway_proxy_integration import (
  Request,
  Response
)

class Controller:
    """
    Controller class to prepare a response based on a request
    """

    def __init__(self, event: dict):
        """
        Initialise class
        """
        self.request = Request(event=event)
        self.response = Response(use_default_cors_headers=True)


    def run(self):
        """
        Processes requests, executes appropriate callbacks and returns response
        """

        method = self.request.method.lower()

        if method == 'get':
            self.process_get_request()

        if method == 'post':
            self.process_post_request()

        if method == 'put':
            self.process_put_request()

        if method == 'patch':
            self.process_patch_request()

        if method == 'delete':
            self.process_delete_request()

        return self.response


    def process_get_request(self):
        """
        Process GET requests.
        Handle retrieval of both a single record as well as multiple records.
        """

        self.response.status_code = 200
        self.response.body = {
            'result': 'read via GET'
        }


    def process_post_request(self):
        """
        Process POST requests.
        POST requests will generate UIDs server side
        """

        self.response.status_code = 201
        self.response.body = {
            'result': 'created via POST'
        }


    def process_put_request(self):
        """
        Process PUT request.
        PUT requests expect the client to provider UIDs
        """

        self.response.status_code = 201
        self.response.body = {
            'result': 'created via PUT'
        }


    def process_patch_request(self):
        """
        Process PATCH request.
        """

        self.response.status_code = 200
        self.response.body = {
            'result': 'updated via PATCH'
        }


    def process_delete_request(self):
        """
        Process DELETE request.
        """

        self.response.status_code = 204
