"""
Test JSON transformation for lambda proxy integration response
"""

from uuid import uuid4
from datetime import date, datetime
from decimal import Decimal
from pygrestqlambda.aws.lambda_function.json_transform import to_string


def test_uuid():
    """
    Test UUIDs are transformed correctly
    """

    uid = uuid4()

    assert to_string(uid) == str(uid)


def test_datetime():
    """
    Test UUIDs are transformed correctly
    """

    now = datetime.now()

    assert to_string(now) == now.isoformat()


def test_date():
    """
    Test dates are transformed correctly
    """

    today = date.today()
    assert to_string(today) == today.isoformat()


def test_decimal():
    """
    Test decimals are transformed correctly
    """

    assert to_string(Decimal('1.0005')) == 1.0005
    assert to_string(Decimal('1.00050')) == 1.0005
