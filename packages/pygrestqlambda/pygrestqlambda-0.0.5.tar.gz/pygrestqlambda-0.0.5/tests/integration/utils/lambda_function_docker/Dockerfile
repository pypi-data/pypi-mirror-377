FROM public.ecr.aws/lambda/python:3

COPY . .

RUN pip install .[dev]

RUN python -m build

CMD [ "tests.integration.utils.lambda_function_docker.app.handler" ]
