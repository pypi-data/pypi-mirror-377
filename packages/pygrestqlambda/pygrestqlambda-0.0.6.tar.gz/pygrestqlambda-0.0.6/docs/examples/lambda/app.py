"""
Lambda handler
"""

import logging
from pygrestqlambda.aws.lambda_function.rest_api_gateway_proxy_integration import Response

def handler(event: dict, context: dict):
    """
    Lambda handler to return supplied JSON in a format expected by AWS REST API Gateway
    """

    logging.debug(context)
    response = Response(
        body={
            'hello': 'from lambda handler',
            'original_input': event
        },
        status_code=200,
    )
    payload = response.get_payload()

    return payload
