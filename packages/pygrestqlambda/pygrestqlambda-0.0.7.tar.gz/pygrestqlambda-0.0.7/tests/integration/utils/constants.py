"""
Integration testing constants, e.g. database connection parameters used by database server
containers and test clients.
"""

from uuid import uuid4

UID = str(uuid4())
POSTGRES_NAME = f'pytest-postgres-{UID}'
MYSQL_NAME = f'pytest-mysql-{UID}'
LAMBDA_FUNCTION_NAME = f'pytest-lambda-{UID}'

DB_NAME = 'pytest'
USERNAME = 'pytest'
PASSWORD = 'pytest'
