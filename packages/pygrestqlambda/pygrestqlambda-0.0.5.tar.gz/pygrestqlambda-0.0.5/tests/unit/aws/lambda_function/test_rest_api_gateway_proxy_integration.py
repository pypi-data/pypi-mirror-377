"""
Test REST API Gateway lambda proxy integration response
"""

import base64
import json
from pygrestqlambda.aws.lambda_function.rest_api_gateway_proxy_integration import Response


def test_json_response():
    """
    Test JSON response is prepared correctly
    """

    response = Response()
    response.body = {'hello': 'world'}

    payload = response.get_payload()

    print(payload)

    assert response.headers['Content-Type'] == 'application/json'
    assert payload['headers']['Content-Type'] == 'application/json'
    assert json.loads(payload['body'])['hello'] == 'world'


def test_plan_text_response():
    """
    Test plain text response is correctly prepared
    """

    response = Response(
        body='hello world',
    )

    payload = response.get_payload()

    assert response.headers['Content-Type'] == 'text/plain'
    assert payload['headers']['Content-Type'] == 'text/plain'
    assert payload['body'] == 'hello world'


def test_binary_response():
    """
    Test binary response is correctly prepared
    """

    response = Response(
        body=b'hello world',
        headers={
            'Content-Type': 'application/pdf',
        },
        is_base64_encoded=True
    )

    payload = response.get_payload()

    assert response.headers['Content-Type'] == 'application/pdf'
    assert payload['headers']['Content-Type'] == 'application/pdf'
    assert base64.b64decode(payload['body']) == b'hello world'


def test_no_cors_headers_by_default():
    """
    Ensure that by default no CORS headers are set
    """

    response = Response()

    headers = response.get_payload()['headers']
    assert "Access-Control-Allow-Origin" not in headers
    assert "Access-Control-Allow-Methods" not in headers
    assert "Access-Control-Allow-Headers" not in headers


def test_default_cors_headers_if_set():
    """
    Ensure that default CORS headers are returned if requested
    """

    response = Response(
        use_default_cors_headers=True
    )

    headers = response.get_payload()['headers']
    assert headers["Access-Control-Allow-Origin"] == "*"
    assert headers["Access-Control-Allow-Methods"] == "*"
    assert headers["Access-Control-Allow-Headers"] == "*"


def test_default_cors_headers_no_override():
    """
    Ensure that any supplied CORS headers are not overwritten if default CORS behaviour
    is enabled.
    """

    response = Response(
        use_default_cors_headers=True,
        headers={
            "Access-Control-Allow-Methods": "ABC",
        },
    )

    headers = response.get_payload()['headers']
    assert headers["Access-Control-Allow-Origin"] == "*"
    assert headers["Access-Control-Allow-Methods"] == "ABC"
    assert headers["Access-Control-Allow-Headers"] == "*"
