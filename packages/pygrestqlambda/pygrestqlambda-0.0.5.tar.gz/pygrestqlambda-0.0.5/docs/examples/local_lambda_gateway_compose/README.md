# REST API Gateway Lambda function docker compose example

Navigate to the current directory from the root of this project:
```shell
cd docs/examples/local_lambda_gateway_compose
```

Start the stack with:
```shell
docker compose up --build
```

In another terminal, make a request to the example endpoint:
```shell
curl http://127.0.0.1:9096/example
```

The following response should be returned:
```json
{
    "hello": "through local OpenAPI REST gateway"
}
```
