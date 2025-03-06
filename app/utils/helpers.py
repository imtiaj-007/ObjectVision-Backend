import random
import string
import json
from datetime import datetime


def generate_otp(otp_length: int = 6, is_alpha_numeric: bool = False) -> str:
    """
    Generates a random OTP (One-Time Password).

    Args:
        otp_length (int): Length of the OTP. Default is 6.
        is_alpha_numeric (bool): 
            If True, generates an alphanumeric OTP. 
            If False, generates a numeric OTP. Default is False.

    Returns:
        str: The generated OTP.
    """
    if otp_length <= 0:
        raise ValueError("OTP length must be greater than 0")

    if is_alpha_numeric:
        characters = string.ascii_uppercase + string.digits  # Alphanumeric characters
    else:
        characters = string.digits  # Numeric characters only

    otp = ''.join(random.choices(characters, k=otp_length))
    return otp


def serialize_datetime(obj):
    """Helper function to convert datetime to string"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj

def serialize_datetime_object(data_entity):
    return json.loads(json.dumps(data_entity, default=serialize_datetime))