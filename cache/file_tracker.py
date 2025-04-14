import os
import json
import redis
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Set, Tuple
from app.configuration.redis_client import get_redis_instance
from app.utils.logger import log


class FileTracker:
    """
    A class to track local file links with a configurable expiry time using Redis.
    Files are deleted by a Celery Beat task after the expiry period.
    """

    def __init__(
        self,
        redis_instance: redis.Redis,
        redis_prefix: str = "file_tracker:",
        expire_time: int = 3600,
        batch_size: int = 100,
    ):
        """
        Initialize the FileTracker with Redis connection.

        Args:
            redis_instance: Redis client instance to use
            redis_prefix: Prefix for Redis keys
            expire_time: Time in seconds until tracked files expire (default: 1 hour)
            batch_size: Size of batches for Redis operations (default: 100)
        """
        self.redis_client = redis_instance
        self.redis_prefix = redis_prefix
        self.expire_time = expire_time
        self.batch_size = batch_size

    def _get_redis_key(self, file_path: str) -> str:
        """Generate Redis key for a file path"""
        # Normalize path for consistent key generation
        normalized_path = os.path.normpath(file_path).replace("\\", "/")
        return f"{self.redis_prefix}{normalized_path}"

    def add_file(self, file_path: Union[str, Path]) -> bool:
        """
        Add a file to the tracking system with expiry.

        Args:
            file_path: Path to the file to track

        Returns:
            bool: True if file was added successfully, False otherwise
        """
        file_path_str = str(file_path)
        if not os.path.exists(file_path_str):
            log.warning(f"File not found: {file_path_str}")
            return False

        # Store file path in Redis with expiry
        key = self._get_redis_key(file_path_str)
        file_info = json.dumps(
            {"path": file_path_str, "added_at": datetime.now().isoformat()}
        )

        try:
            pipe = self.redis_client.pipeline()
            pipe.set(key, file_info)
            pipe.expire(key, self.expire_time)
            pipe.execute()
            log.info(
                f"Added file to tracking: {file_path_str}, expires in {self.expire_time}s"
            )
            return True
        except redis.RedisError as e:
            log.error(f"Redis error when adding file {file_path_str}: {str(e)}")
            return False

    def get_expiry_time(self, file_path: Union[str, Path]) -> Optional[datetime]:
        """
        Get the expiry time for a tracked file.

        Args:
            file_path: Path to the file

        Returns:
            Optional[datetime]: Expiry time or None if file is not tracked
        """
        file_path_str = str(file_path)
        key = self._get_redis_key(file_path_str)
        try:
            ttl = self.redis_client.ttl(key)
            if ttl > 0:
                # Convert TTL (seconds remaining) to datetime
                return datetime.now() + timedelta(seconds=ttl)
        except redis.RedisError as e:
            log.error(
                f"Redis error when getting expiry time for {file_path_str}: {str(e)}"
            )
        return None

    def _get_tracked_file_paths(self) -> Set[str]:
        """
        Get set of all tracked file paths.

        Returns:
            Set[str]: Set of file paths that are tracked in Redis
        """
        tracked_files = set()
        cursor = 0

        try:
            while True:
                cursor, keys = self.redis_client.scan(
                    cursor=cursor, match=f"{self.redis_prefix}*", count=self.batch_size
                )

                if keys:
                    # Using pipeline for bulk operations
                    pipe = self.redis_client.pipeline()
                    for key in keys:
                        pipe.get(key)
                    results = pipe.execute()

                    for file_info in results:
                        if file_info:
                            try:
                                file_data = json.loads(file_info)
                                tracked_files.add(file_data["path"])
                            except (json.JSONDecodeError, KeyError) as e:
                                log.warning(f"Error parsing file info: {str(e)}")

                if cursor == 0:
                    break
        except redis.RedisError as e:
            log.error(f"Redis error when getting tracked files: {str(e)}")

        return tracked_files

    def get_expired_files(self, base_directory: Union[str, Path]) -> List[str]:
        """
        Get a list of files in the directory that are not tracked in Redis.

        Args:
            base_directory: Directory to check for untracked files

        Returns:
            List[str]: List of file paths that are not tracked in Redis
        """
        base_dir_str = str(base_directory)

        # Get all tracked files
        tracked_files = self._get_tracked_file_paths()

        # Check base directory for files not in tracking
        expired_files = []
        try:
            base_dir_path = Path(base_dir_str)
            if base_dir_path.exists():
                for file_path in base_dir_path.glob("**/*"):
                    if file_path.is_file():
                        file_path_str = str(file_path)
                        if file_path_str not in tracked_files:
                            expired_files.append(file_path_str)
        except Exception as e:
            log.error(f"Error scanning directory {base_dir_str}: {str(e)}")

        return expired_files

    def delete_expired_files(self, base_directory: Union[str, Path]) -> int:
        """
        Delete all files in the specified directory that are not tracked in Redis.

        Args:
            base_directory: Directory to check for untracked files

        Returns:
            int: Number of files deleted
        """
        base_dir_str = str(base_directory)
        files_deleted = 0

        # Handle Windows paths correctly
        base_dir_str = os.path.normpath(base_dir_str)

        if not os.path.exists(base_dir_str):
            log.warning(f"Base directory does not exist: {base_dir_str}")
            return 0

        # Get files that are not tracked in Redis
        expired_files = self.get_expired_files(base_dir_str)

        # Delete files that are not tracked
        for file_path in expired_files:
            try:
                os.remove(file_path)
                log.info(f"Deleted expired file: {file_path}")
                files_deleted += 1
            except OSError as e:
                log.error(f"Error deleting {file_path}: {str(e)}")

        # Get keys that are about to expire and delete their files proactively
        soon_expired_files = self._get_soon_expired_files(
            60
        )  # Files expiring in next 60 seconds

        for file_path in soon_expired_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    # Also remove from Redis immediately
                    key = self._get_redis_key(file_path)
                    self.redis_client.delete(key)
                    log.info(f"Proactively deleted soon-to-expire file: {file_path}")
                    files_deleted += 1
            except Exception as e:
                log.error(f"Error proactively deleting {file_path}: {str(e)}")

        return files_deleted

    def _get_soon_expired_files(self, seconds_threshold: int = 60) -> List[str]:
        """
        Get files that will expire soon.

        Args:
            seconds_threshold: Time threshold in seconds (default: 60)

        Returns:
            List[str]: List of file paths that will expire soon
        """
        soon_expired = []
        cursor = 0

        try:
            while True:
                cursor, keys = self.redis_client.scan(
                    cursor=cursor, match=f"{self.redis_prefix}*", count=self.batch_size
                )

                if keys:
                    # Using pipeline for bulk operations
                    pipe = self.redis_client.pipeline()
                    for key in keys:
                        pipe.ttl(key)
                    ttls = pipe.execute()

                    # Get file info for keys that will expire soon
                    soon_expire_keys = [
                        key
                        for key, ttl in zip(keys, ttls)
                        if 0 < ttl < seconds_threshold
                    ]

                    if soon_expire_keys:
                        pipe = self.redis_client.pipeline()
                        for key in soon_expire_keys:
                            pipe.get(key)
                        file_infos = pipe.execute()

                        for file_info in file_infos:
                            if file_info:
                                try:
                                    file_data = json.loads(file_info)
                                    soon_expired.append(file_data["path"])
                                except (json.JSONDecodeError, KeyError) as e:
                                    log.warning(f"Error parsing file info: {str(e)}")

                if cursor == 0:
                    break
        except redis.RedisError as e:
            log.error(f"Redis error when getting soon expired files: {str(e)}")

        return soon_expired

    def get_all_tracked_files(self) -> List[Dict[str, Union[str, int]]]:
        """
        Get a list of all currently tracked files with their expiry times.

        Returns:
            List[Dict]: List of dictionaries with file information
        """
        result = []
        cursor = 0

        try:
            while True:
                cursor, keys = self.redis_client.scan(
                    cursor=cursor, match=f"{self.redis_prefix}*", count=self.batch_size
                )

                if keys:
                    # Use pipeline for batch operations
                    pipe = self.redis_client.pipeline()
                    for key in keys:
                        pipe.get(key)
                        pipe.ttl(key)
                    results = pipe.execute()

                    # Process results in pairs (get, ttl)
                    for i in range(0, len(results), 2):
                        file_info = results[i]
                        ttl = results[i + 1]

                        if file_info and ttl > 0:
                            try:
                                file_data = json.loads(file_info)
                                result.append(
                                    {
                                        "path": file_data["path"],
                                        "added_at": file_data["added_at"],
                                        "expires_in_seconds": ttl,
                                        "expires_at": (
                                            datetime.now() + timedelta(seconds=ttl)
                                        ).isoformat(),
                                    }
                                )
                            except (json.JSONDecodeError, KeyError) as e:
                                log.warning(f"Error processing key: {str(e)}")

                if cursor == 0:
                    break
        except redis.RedisError as e:
            log.error(f"Redis error when getting all tracked files: {str(e)}")

        return result

    def bulk_add_files(self, file_paths: List[Union[str, Path]]) -> Tuple[int, int]:
        """
        Add multiple files to tracking in a single batch operation.

        Args:
            file_paths: List of file paths to track

        Returns:
            Tuple[int, int]: (Number of files added successfully, total files)
        """
        if not file_paths:
            return 0, 0

        success_count = 0

        try:
            pipe = self.redis_client.pipeline()
            now = datetime.now().isoformat()

            for file_path in file_paths:
                file_path_str = str(file_path)
                if os.path.exists(file_path_str):
                    key = self._get_redis_key(file_path_str)
                    file_info = json.dumps({"path": file_path_str, "added_at": now})
                    pipe.set(key, file_info)
                    pipe.expire(key, self.expire_time)
                    success_count += 1

            if success_count > 0:
                pipe.execute()
                log.info(
                    f"Bulk added {success_count}/{len(file_paths)} files to tracking"
                )
        except redis.RedisError as e:
            log.error(f"Redis error during bulk add: {str(e)}")

        return success_count, len(file_paths)

    def remove_from_tracking(self, file_path: Union[str, Path]) -> bool:
        """
        Remove a file from tracking without deleting it.

        Args:
            file_path: Path to the file to remove from tracking

        Returns:
            bool: True if file was removed from tracking, False if not found
        """
        file_path_str = str(file_path)
        key = self._get_redis_key(file_path_str)
        try:
            if self.redis_client.exists(key):
                self.redis_client.delete(key)
                log.info(f"Removed file from tracking: {file_path_str}")
                return True
        except redis.RedisError as e:
            log.error(f"Redis error when removing file {file_path_str}: {str(e)}")
        return False

    def cleanup_all_directories(self, base_directories: List[Union[str, Path]]) -> int:
        """
        Delete expired files from multiple directories in one operation.

        Args:
            base_directories: List of directories to clean up

        Returns:
            int: Total number of files deleted
        """
        total_deleted = 0

        for directory in base_directories:
            try:
                dir_str = str(directory)
                deleted = self.delete_expired_files(dir_str)
                total_deleted += deleted
                log.info(f"Deleted {deleted} expired files from {dir_str}")
            except Exception as e:
                log.error(f"Error cleaning up directory {directory}: {str(e)}")

        return total_deleted


# Global file_tracker instance
redis_client = get_redis_instance()
local_file_tracker = FileTracker(redis_client)
