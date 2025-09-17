"""
Pytest configuration file, sets up fixtures to be re-used and set up pre-test
configuration.
Uses [docker](https://docker-py.readthedocs.io/en/stable/index.html) python
client to manage container.
"""

from pytest import fixture
from tests.integration.utils.constants import POSTGRES_NAME, LAMBDA_FUNCTION_NAME
from tests.integration.utils.db_postgres import get_postgres_connection
from tests.integration.utils.lambda_function import get_base_url
from tests.integration.utils.docker import remove_container

@fixture(scope="session")
def postgres():
    """
    Return a psycopg database connection
    """

    return get_postgres_connection()


@fixture(scope="session")
def lambda_function_url():
    """
    Return a lambda function for making requests to
    """

    return get_base_url()


def pytest_sessionfinish():
    """
    Runs after all tests have completed
    Tear down containers.
    """

    remove_container(POSTGRES_NAME)
    remove_container(LAMBDA_FUNCTION_NAME)
