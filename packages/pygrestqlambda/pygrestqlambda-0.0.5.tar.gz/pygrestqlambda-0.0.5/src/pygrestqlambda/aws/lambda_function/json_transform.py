"""
JSON output transformer for non-serialisable values
"""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

def to_string(value: object) -> str:
    """
    Calculates the string version of an object to return in a JSON response
    """

    # Handle UUIDs
    if isinstance(value, UUID):
        value = str(value)

    # Handle date/timestamps
    if isinstance(value, datetime):
        value = value.isoformat()

    if isinstance(value, date):
        value = value.isoformat()

    # Handle decimals
    if isinstance(value, Decimal):
        value = float(value)

    return value
