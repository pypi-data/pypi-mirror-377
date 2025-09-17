from pygrestqlambda.aws.lambda_function.rest_api_gateway_proxy_integration import Response

response = Response(
    body = {
        'hello': 'world'
    }
)

print(response.get_payload())
