"""
Database connection tests
"""

from psycopg.connection import Connection

def test_postgres(postgres: Connection):
    """
    Test whether a connection to a local postgres Docker container can be established.
    """

    result = postgres.execute("select 8 + 4 AS twelve").fetchone()
    assert result['twelve'] == 12
