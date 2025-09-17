"""
Lambda function handler to be used in integration tests
"""

import logging
from pygrestqlambda.aws.lambda_function.rest_api_gateway_proxy_integration import Response

def handler(event, context):
    """
    Lambda function handler
    """

    logging.debug(event)
    logging.debug(context)

    payload = Response(
        body='hello world'
    ).get_payload()

    return payload
