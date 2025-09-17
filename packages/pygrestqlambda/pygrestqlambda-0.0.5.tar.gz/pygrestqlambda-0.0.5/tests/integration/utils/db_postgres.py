"""
Postgres database Docker integration testing utilities for set up and tear down
"""

import docker
from docker.models.containers import Container
from docker.errors import NotFound
import psycopg
from psycopg.connection import Connection
from psycopg.rows import dict_row
from tests.integration.utils.constants import POSTGRES_NAME, DB_NAME, USERNAME, PASSWORD
from tests.integration.utils.docker import wait_for_healthy_container


def create_postgres_container() -> Container:
    """
    Create a postgres container
    """

    # Create postgres container
    client = docker.from_env()
    container = client.containers.run(
        image='postgres:17',
        name=POSTGRES_NAME,
        detach=True,
        ports={'5432/tcp': None},
        environment={
            'POSTGRES_DB': DB_NAME,
            'POSTGRES_USER': USERNAME,
            'POSTGRES_PASSWORD': PASSWORD,
        },
        healthcheck={
            "test": "psql -h localhost -U $POSTGRES_USER -c 'select 3 + 2;'",
            "interval": 1000000000, # 1 second in nanoseconds
            "retries": 20,
        },
        command="""
            -c ssl=on
            -c ssl_cert_file=/etc/ssl/certs/ssl-cert-snakeoil.pem
            -c ssl_key_file=/etc/ssl/private/ssl-cert-snakeoil.key
        """
    )

    return container


def get_postgres_container(create: bool = True) -> Container | None:
    """
    Return the running postgres Docker container, starting one if none exist
    """

    client = docker.from_env()

    try:
        container = client.containers.get(container_id=POSTGRES_NAME)
    except NotFound:
        if create:
            container = create_postgres_container()
        else:
            return None

    wait_for_healthy_container(container=container)

    return container


def get_postgres_connection() -> Connection:
    """
    Return a connection to the running postgres container
    """

    container = get_postgres_container()

    connection = psycopg.connect(
        host='127.0.0.1',
        port=container.ports['5432/tcp'][0]['HostPort'],
        user=USERNAME,
        password=PASSWORD,
        dbname=DB_NAME,
        sslmode='require',
    )

    connection.row_factory = dict_row

    return connection
