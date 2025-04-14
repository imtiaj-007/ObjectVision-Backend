import redis
from datetime import datetime, timezone
from typing import Dict, Optional
from pydantic import BaseModel, ValidationError

from app.configuration.redis_client import get_redis_instance
from app.schemas.enums import ActivityTypeEnum
from app.schemas.user_activity_schemas import UserActivityResponse
from app.utils.logger import log


class UserActivityNotFoundError(Exception):
    """Exception raised when user activity is not found"""

    pass


class UserActivityValidationError(Exception):
    """Exception raised when user activity data is invalid"""

    pass


class UserActivity(BaseModel):
    username: str
    activities: Dict[ActivityTypeEnum, Optional[UserActivityResponse]] = {}
    last_updated: datetime = datetime.now(timezone.utc)


class UserActivityTracker:
    """
    UserActivityTracker class to store user activities.
    It acts as an cache to improve performane and reduce frequent DB quering.
    """

    def __init__(
        self,
        redis_instance: redis.Redis,
        redis_prefix: str = "user_activity",
        expire_time: int = 900,
    ):
        self.redis = redis_instance
        self.redis_prefix = redis_prefix
        self.expire_time = expire_time

    def _get_redis_key(self, username: str) -> str:
        return f"{self.redis_prefix}:{username}"

    def get_user(self, username: str) -> Optional[UserActivity]:
        """Fetch a user's activity data from Redis"""
        user_data = self.redis.get(self._get_redis_key(username))
        if not user_data:
            return None
        try:
            return UserActivity.model_validate_json(user_data)

        except ValidationError as e:
            log.warning(f"Invalid user data for {username}: {str(e)}")
            raise UserActivityValidationError(f"Invalid user data format: {str(e)}")

    def create_user(self, username: str) -> UserActivity:
        """Create a new user in Redis"""
        user = UserActivity(username=username)
        self.redis.setex(
            self._get_redis_key(username), self.expire_time, user.model_dump_json()
        )
        return user

    def store_activity(
        self, username: str, activity: UserActivityResponse
    ) -> UserActivityResponse:
        """Store a new activity for a user in Redis"""
        key = self._get_redis_key(username)
        user = self.get_user(username) or UserActivity(username=username)
        user.activities[activity.activity_type] = activity
        user.last_updated = datetime.now(timezone.utc)
        self.redis.setex(key, self.expire_time, user.model_dump_json())
        return activity

    def get_activities(
        self, username: str, activity_type: Optional[ActivityTypeEnum] = None
    ) -> Dict[ActivityTypeEnum, Optional[UserActivityResponse]]:
        """Fetch user activities from Redis"""
        user = self.get_user(username)
        if not user:
            return {}
        return (
            {activity_type: user.activities[activity_type]}
            if activity_type
            else user.activities
        )

    def remove_activity(self, username: str, activity_type: ActivityTypeEnum) -> bool:
        """Remove a specific activity for a user"""
        user = self.get_user(username)
        if not user or activity_type not in user.activities:
            return False
        user.activities[activity_type] = None
        self.redis.setex(
            self._get_redis_key(username), self.expire_time, user.model_dump_json()
        )
        return True

    def remove_user(self, username: str) -> bool:
        """Remove a user and all their activities from Redis"""
        return bool(self.redis.delete(self._get_redis_key(username)))


# Global activity_tracker instance
redis_client = get_redis_instance()
user_activity_tracker = UserActivityTracker(redis_client)
