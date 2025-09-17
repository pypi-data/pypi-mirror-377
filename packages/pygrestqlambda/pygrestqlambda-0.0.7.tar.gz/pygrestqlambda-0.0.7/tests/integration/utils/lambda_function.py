"""
Lambda function Docker integration testing utilities for set up and tear down
"""

from os.path import join
from pathlib import Path

import docker
from docker.models.containers import Container
from docker.errors import NotFound

from tests.integration.utils.constants import LAMBDA_FUNCTION_NAME
from tests.integration.utils.docker import wait_for_healthy_container

def create_lambda_container() -> Container:
    """
    Create a lambda function container
    """

    # Create postgres container
    client = docker.from_env()

    context_path = str(Path(__file__).parent.parent.parent.parent)
    dockerfile_path = join('tests', 'integration', 'utils', 'lambda_function_docker', 'Dockerfile')

    image, _ = client.images.build(
        path=context_path,
        dockerfile=dockerfile_path,
        tag="pygrestqlambda",
    )

    container = client.containers.run(
        image=image.id,
        name=LAMBDA_FUNCTION_NAME,
        detach=True,
        ports={"8080/tcp": None},
        environment={},
        healthcheck={
            "test": "curl -d '{}' 127.0.0.1:8080/2015-03-31/functions/function/invocations",
            "interval": 1000000000,  # 1 second in nanoseconds
            "retries": 20,
        },
    )

    # return container
    return container


def get_lambda_container(create: bool = True) -> Container | None:
    """
    Return the running lambda function Docker container, starting one if none exist
    """

    client = docker.from_env()

    try:
        container = client.containers.get(container_id=LAMBDA_FUNCTION_NAME)
    except NotFound:
        if create:
            container = create_lambda_container()
        else:
            return None

    wait_for_healthy_container(container=container)

    return container


def get_base_url() -> str:
    """
    Get the base URL of lambda function, needed because port number is dynamic
    """

    container = get_lambda_container()
    port = container.ports['8080/tcp'][0]['HostPort']
    base_url = f"http://127.0.0.1:{port}/2015-03-31/functions/function/invocations"

    return base_url
