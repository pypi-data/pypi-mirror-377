from pygrestqlambda.aws.lambda_function.rest_api_gateway_proxy_integration import Response

response = Response(
    headers={'Content-Type': 'text/html'},
    body = 'hello'
)

print(response.get_payload())
