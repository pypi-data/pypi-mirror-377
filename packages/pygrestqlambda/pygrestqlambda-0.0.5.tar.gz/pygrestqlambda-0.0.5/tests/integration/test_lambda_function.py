"""
Database connection tests
"""

import httpx

def test_lambda_function(lambda_function_url: str):
    """
    Test whether a connection to a built local lambda function can be established
    """


    response = httpx.post(url=lambda_function_url, json={})
    assert response.json()['body'] == 'hello world'
