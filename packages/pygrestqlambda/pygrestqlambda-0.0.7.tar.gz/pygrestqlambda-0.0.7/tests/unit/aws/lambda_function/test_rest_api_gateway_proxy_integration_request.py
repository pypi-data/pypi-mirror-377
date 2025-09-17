"""
Test REST API Gateway lambda proxy integration response
"""

import json
from pathlib import Path
from pygrestqlambda.aws.lambda_function.rest_api_gateway_proxy_integration import Request


def test_request_nonbase64():
    """
    Test non-base64 request is correctly parsed
    """

    path = Path(__file__).parent.joinpath('fixtures', 'non-base64-request.json')
    fixture = path.read_text(encoding='utf-8')

    request = Request(json.loads(fixture))

    assert request.resource == '/example'
    assert request.cognito_uid is None


def test_request_base64():
    """
    Test non-base64 request is correctly parsed
    """

    path = Path(__file__).parent.joinpath('fixtures', 'base64-request.json')
    fixture = path.read_text(encoding='utf-8')

    request = Request(json.loads(fixture))

    assert request.body == {"example": "value"}


def test_request_empty_event():
    """
    Assert no event behaviour
    """

    request = Request({})

    # Assert authorisation
    assert request.cognito_uid is None
    # Assert headers for body and response
    assert request.accept is None
    assert request.content_type is None
    # Assert resource is None
    assert request.resource is None
    assert request.method is None
    # Extract parameters
    assert request.query_params is None
    assert request.path_params is None
    # Extract body
    assert request.body is None


def test_request_empty_content_type():
    """
    Assert no event behaviour
    """

    request = Request({
        'headers': {},
        'body': 'example',
    })

    assert request.accept is None
    assert request.content_type is None


def test_request_plan_text():
    """
    Assert no event behaviour
    """

    request = Request({
        'headers': {
            'content-type': 'text/plain'
        },
        'body': 'example',
    })

    assert request.content_type == 'text/plain'
    assert request.body == 'example'


def test_cognito_uid():
    """
    Assert retrieving Cognito UID
    """

    request = Request({
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': 'abc123'
                },
            },
        }
    })

    assert request.cognito_uid == 'abc123'


def test_no_content_type_header():
    """
    Assert no event behaviour
    """

    request = Request({
        'headers': {
            'content-type': 'unknown/unknown'
        },
        'body': 'example',
    })

    assert request.content_type == 'unknown/unknown'
    assert request.body == 'example'
