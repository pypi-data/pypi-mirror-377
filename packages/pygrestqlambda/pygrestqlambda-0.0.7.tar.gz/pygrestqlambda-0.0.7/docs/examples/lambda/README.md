# Lambda function docker container example

Navigate to the current directory from the root of this project:
```shell
cd docs/examples/lambda
```

From the current directory, build image with:
```shell
docker build -t pygrestqlambda/lambda .
```

The run the container with:
```shell
docker run -p 9095:8080 pygrestqlambda/lambda
```

In a separate terminal, run the following commands:
```shell
curl \
    -X POST \
    -d '{"hello": "from terminal"}' \
    http://127.0.0.1:9095/2015-03-31/functions/function/invocations
```

The following is returned:
```json
{
    "isBase64Encoded": false,
    "statusCode": 200,
    "headers": {"Content-Type": "application/json"},
    "multiValueHeaders": null,
    "body": "{\"hello\": \"from lambda handler\", \"original_input\": {\"hello\": \"from terminal\"}}"
}
```
