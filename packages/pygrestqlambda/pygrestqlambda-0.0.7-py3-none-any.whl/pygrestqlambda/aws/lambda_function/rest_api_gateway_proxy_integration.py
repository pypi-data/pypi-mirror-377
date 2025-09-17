"""
Receives payload in format sent by AWS REST API Gateway
https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

Returns payload structure expected by REST API Gateway
https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-output-format
"""

from base64 import b64encode, b64decode
from dataclasses import dataclass
import json
import logging
from pygrestqlambda.aws.lambda_function.json_transform import to_string


@dataclass
class Response:
    """
    Lambda function proxy response for REST API Gateway
    """
    is_base64_encoded: bool | None = False
    status_code: int | None = 401
    headers: dict | None = None
    multi_value_headers: dict | None = None
    body: str | dict | None = None
    use_default_cors_headers: bool = False


    def get_default_cors_headers(self) -> dict:
        """
        Return default CORS headers
        """

        cors_headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*"
        }

        return cors_headers


    def get_payload(self) -> dict:
        """
        Gets payload to send to REST API Gateway
        """

        is_json = False
        if isinstance(self.body, dict):
            is_json = True

        # Set headers
        if self.headers is None:
            self.headers = {}

        if "Content-Type" not in self.headers:
            logging.debug("No content type header set")
            if is_json:
                logging.debug("Using application/json for content-type")
                self.headers["Content-Type"] = "application/json"
            else:
                logging.debug("Using text/plain for content-type")
                self.headers["Content-Type"] = "text/plain"

        # Optionally include CORS headers
        if self.use_default_cors_headers:
            for key, value in self.get_default_cors_headers().items():
                if key not in self.headers:
                    self.headers[key] = value

        # Calculate body
        if self.is_base64_encoded:
            body = b64encode(self.body).decode("utf-8")
        else:
            if is_json:
                logging.debug("Body is a JSON object")
                body = json.dumps(self.body, default=to_string)
            else:
                logging.debug("Body is plain text")
                body = self.body

        logging.debug("Transforming dataclass dictionary to JSON")
        data = {
            "isBase64Encoded": self.is_base64_encoded,
            "statusCode": self.status_code,
            "headers": self.headers,
            "multiValueHeaders": self.multi_value_headers,
            "body": body,
        }

        return data

# pylint: disable=too-many-instance-attributes
class Request:
    """
    Lambda function proxy integration request
    """

    def __init__(self, event: dict):
        self.event = event
        # Extract authorisation information
        self.cognito_uid = self.get_cognito_uid()
        # Extract headers needed for body and response
        self.accept: str = self.get_header('accept')
        self.content_type: str = self.get_header('content-type')
        # Extract resource
        self.resource = event.get('resource')
        self.method = event.get('httpMethod')
        # Extract parameters
        self.query_params = event.get('multiValueQueryStringParameters')
        self.path_params = event.get('pathParameters')
        # Extract body
        self.body = self.get_body()


    def get_body(self):
        """
        Returns body from request, decodes from base64 if necessary
        """

        body = self.event.get('body')
        content = body
        if self.event.get('isBase64Encoded'):
            if body:
                content = b64decode(body)

        # Handle no content type
        if self.content_type is None:
            return content

        # Handle plain text
        if self.content_type.lower() == 'text/plain':
            return str(content)

        # Handle JSON
        if self.content_type.lower() == 'application/json':
            return json.loads(content)

        return content


    def get_cognito_uid(self):
        """
        Retrieve Cognito UID from supplied claim
        """
        claims = self.event.get('requestContext', {}).get('authorizer', {}).get('claims')

        if claims is None:
            logging.info('No claims in event request context authoriser')
            return None

        cognito_uid = claims.get('sub')

        return cognito_uid


    def get_header(self, header_name: str):
        """
        Retrieve Accept header
        """

        headers = self.event.get('headers')
        if headers is None:
            return None

        # Lowercase all the headers
        headers_lower = {k.lower():v for k,v in headers.items()}

        accept = headers_lower.get(header_name.lower())

        return accept
