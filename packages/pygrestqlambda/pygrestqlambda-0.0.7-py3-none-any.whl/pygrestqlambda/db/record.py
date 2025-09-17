"""
Record that represents a DB table row
"""

from abc import ABCMeta


class Record(metaclass=ABCMeta):
    """
    Generic record that maps to a row in a database table
    """

    def __init__(self, conn: bool = False) -> None:
        self.conn = conn

    def before_create(self):
        """
        Runs before a new record is created. Useful for mutating a new record
        before being committed.
        """


    def before_read(self):
        """
        Before a record is retrieved from the database. Useful for injecting
        filters or sorting.
        """


    def before_update(self):
        """
        Before a new record is created. Useful for mutating a record before it
        is committed.
        """


    def before_delete(self):
        """
        Before an existing record is deleted. Useful for e.g. updating counters
        or other aggregate fields in other tables.
        """


    def after_create(self):
        """
        Runs after a new record is created. Useful for updating e.g. counters
        tables.
        """


    def after_read(self):
        """
        After a record is retrieved from the database. Useful for transforming
        retrieved data.
        """


    def after_update(self):
        """
        Runs after a new record is updated. Useful for updating e.g. counters
        tables.
        """


    def after_delete(self):
        """
        Runs after an existing record is deleted. Useful for updating e.g.
        counters tables.
        """
