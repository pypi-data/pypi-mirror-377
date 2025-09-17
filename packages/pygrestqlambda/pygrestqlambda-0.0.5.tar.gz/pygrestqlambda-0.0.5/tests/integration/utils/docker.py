"""
Docker utilities
"""

import logging
from time import sleep
import docker
from docker.errors import NotFound
from docker.models.containers import Container

def wait_for_healthy_container(container: Container) -> None:
    """
    Wait for a container health to become healthy
    """
    max_retries = 20
    logging.info('Waiting for container health to become health with %s retries', max_retries)
    for _ in range(max_retries + 1):
        container.reload()

        logging.info('Container health: %s', container.health)
        if container.health == 'healthy':
            return None

        sleep(1)

    raise TimeoutError(f'Container not healthy after {max_retries} seconds')


def remove_container(name: str):
    """
    Remove container by name
    """

    logging.info('Attempting to stop container %s', name)
    client = docker.from_env()

    try:
        container = client.containers.get(container_id=name)
    except NotFound:
        return

    logging.info('Container state: %s', container.status)

    if container.status == 'running':
        logging.info('Stopping container id: %s', container.id)
        container.stop()

    logging.info('Removing container id: %s', container.id)
    container.remove()
