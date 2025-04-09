import random
import string
import json
from datetime import datetime
from typing import List, Dict, Any
from app.schemas.enums import ActivityTypeEnum
from app.schemas.subscription_schema import SubscriptionDetails


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

    otp = "".join(random.choices(characters, k=otp_length))
    return otp


def serialize_datetime(obj):
    """Helper function to convert datetime to string"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj


def serialize_datetime_object(data_entity):
    return json.loads(json.dumps(data_entity, default=serialize_datetime))


def get_plan_keys(plan_details: SubscriptionDetails):
    limits_map = {}
    for group in plan_details.feature_groups:
        if group.title == "Dashboard & Overview":
            for feature in group.features:
                if feature.key in [
                    "storage",
                    "validity",
                    "image_backup_duration",
                    "video_backup_duration",
                ]:
                    limits_map[feature.key] = feature.numeric_value

        elif group.title == "Image Processing":
            for feature in group.features:
                if feature.key in [
                    "daily_limit",
                    "total_limit",
                    "max_image_size",
                ]:
                    limits_map[f"image_{feature.key}"] = feature.numeric_value

        elif group.title == "Video Processing":
            for feature in group.features:
                if feature.key in [
                    "daily_limit",
                    "total_limit",
                    "max_video_size",
                ]:
                    limits_map[f"video_{feature.key}"] = feature.numeric_value
    return limits_map


def create_activity_entries(
    user_plan_id: int, type_map: Dict[str, Any]
) -> List[Dict[str, Any]]:
    return [
        {
            "active_user_plan_id": user_plan_id,
            "activity_type": ActivityTypeEnum.STORAGE_USAGE,
            "daily_usage": 0,
            "total_usage": 0,
            "daily_limit": None,
            "total_limit": type_map.get("storage", None),
            "max_size": None,
        },
        {
            "active_user_plan_id": user_plan_id,
            "activity_type": ActivityTypeEnum.IMAGE_USAGE,
            "daily_usage": 0,
            "total_usage": 0,
            "daily_limit": type_map.get("image_daily_limit", None),
            "total_limit": type_map.get("image_total_limit", None),
            "max_size": type_map.get("image_max_image_size", None),
        },
        {
            "active_user_plan_id": user_plan_id,
            "activity_type": ActivityTypeEnum.VIDEO_USAGE,
            "daily_usage": 0,
            "total_usage": 0,
            "daily_limit": type_map.get("video_daily_limit", None),
            "total_limit": type_map.get("video_total_limit", None),
            "max_size": type_map.get("video_max_video_size", None),
        },
    ]
