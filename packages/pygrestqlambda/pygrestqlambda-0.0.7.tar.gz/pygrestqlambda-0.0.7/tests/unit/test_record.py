"""
Test DB record
"""

from pygrestqlambda.db.record import Record


def test_record():
    """
    Test record
    """

    record = Record()
    assert record.after_create() is None
