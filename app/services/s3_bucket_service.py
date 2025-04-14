import re
import boto3
from pathlib import Path
from functools import lru_cache
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Optional, Dict, Union
from datetime import datetime
from fastapi import HTTPException, status
from app.configuration.config import settings
from app.helpers.file_types import FileType, FileConfig
from app.utils.logger import log


class S3Config:
    """Configuration class for S3 settings"""

    def __init__(self):
        self.aws_access_key = settings.AWS_ACCESS_KEY
        self.aws_secret_key = settings.AWS_SECRET_ACCESS_KEY
        self.region = settings.AWS_REGION or "ap-south-1"  # South pacific Mumbai
        self.bucket_name = settings.AWS_BUCKET_NAME

        if not all([self.aws_access_key, self.aws_secret_key, self.bucket_name]):
            raise ValueError("Missing required AWS credentials or bucket configuration")


class S3Manager:
    """Class to handle S3 operations with improved error handling and caching"""

    def __init__(self):
        self.config = S3Config()
        self._client = None
        self.SAFE_FILENAME_REGEX = re.compile(r"^[\w\-. ]+$")

    @property
    @lru_cache(maxsize=1)
    def client(self):
        """Cached S3 client initialization"""
        if self._client is None:
            self._client = boto3.client(
                "s3",
                aws_access_key_id=self.config.aws_access_key,
                aws_secret_access_key=self.config.aws_secret_key,
                region_name=self.config.region,
            )
        return self._client

    def _validate_file_params(
        self, folder: str, filename: str, file_type: FileType
    ) -> Dict:
        """Validate file parameters and return file information"""
        if not filename or not folder:
            raise ValueError("Filename and folder must not be empty")

        if not self.SAFE_FILENAME_REGEX.match(filename):
            raise ValueError("Invalid filename format")

        file_path = Path(filename)
        ext = file_path.suffix.lower()
        file_config = FileConfig.CONFIGURATIONS.get(file_type)

        if not file_config:
            raise ValueError(f"Invalid file type: {file_type}")

        if ext not in file_config["extensions"]:
            raise ValueError(
                f"Unsupported file extension for {file_type.value}. Allowed: {file_config['extensions']}"
            )

        return {
            "extension": ext,
            "mime_type": file_config["mime_types"].get(ext),
            "max_size": file_config["max_size"],
        }

    def _build_file_key(self, folder: str, filename: str) -> str:
        """Build and sanitize the file key using Path"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = Path(filename)
        base = file_path.stem
        ext = file_path.suffix
        unique_filename = f"{base}_{timestamp}{ext}"

        # Sanitize folder path and convert to S3-compatible format
        safe_folder = Path(folder).as_posix().strip("/")

        return f"{safe_folder}/{unique_filename}"

    def upload_file(
        self,
        local_file_path: str,
        folder: str,
        filename: str = None,
        file_type: FileType = FileType.DOCUMENT,
    ):
        """Upload a file from the local server to S3"""
        file_path = Path(local_file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {local_file_path}")

        filename = filename or file_path.name

        # Validate file parameters and Build a unique S3 key
        self._validate_file_params(folder, filename, file_type)
        file_key = self._build_file_key(folder, filename)

        # Get content type
        ext = file_path.suffix.lower()
        content_type = FileConfig.CONFIGURATIONS[file_type]["mime_types"].get(ext)

        try:
            self.client.upload_file(
                Filename=str(file_path),
                Bucket=self.config.bucket_name,
                Key=file_key,
                ExtraArgs={"ContentType": content_type},
            )

            log.info(f"Successfully uploaded {filename} to S3 at {file_key}")
            return file_key

        except NoCredentialsError as e:
            log.error(f"AWS credentials not found: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="AWS credentials not found",
            )
        except ClientError as e:
            log.error(f"AWS S3 error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error uploading to S3",
            )
        except Exception as e:
            log.error(f"Unexpected error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    def generate_presigned_url(
        self,
        file_key: str,
        operation: str,
        expiration: int = 3600,
        extra_params: Optional[Dict] = None,
    ) -> str:
        """Generate a presigned URL with additional parameters and error handling"""
        try:
            params = {"Bucket": self.config.bucket_name, "Key": file_key}
            if extra_params:
                params.update(extra_params)

            url = self.client.generate_presigned_url(
                ClientMethod=operation, Params=params, ExpiresIn=expiration
            )

            log.info(
                f"Generated presigned URL for operation: {operation}, key: {file_key}"
            )
            return url

        except NoCredentialsError as e:
            log.error(f"AWS credentials not found: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="AWS credentials not found",
            )
        except ClientError as e:
            log.error(f"AWS S3 error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error generating presigned URL",
            )
        except Exception as e:
            log.error(f"Unexpected error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )
        
    def get_upload_url(
        self, folder: str, filename: str, file_type: FileType, expiration: int = 3600
    ) -> Dict[str, Union[str, Dict]]:
        """Generate a presigned URL for uploading files with type-specific validation"""
        file_info = self._validate_file_params(folder, filename, file_type)
        file_key = self._build_file_key(folder, filename)

        extra_params = {
            "ContentType": file_info["mime_type"],
            "ContentLength": file_info["max_size"],
        }

        url = self.generate_presigned_url(
            file_key, "put_object", expiration=expiration, extra_params=extra_params
        )

        return {
            "url": url,
            "file_key": file_key,
            "max_file_size": file_info["max_size"],
            "allowed_extensions": list(
                FileConfig.CONFIGURATIONS[file_type]["extensions"]
            ),
            "content_type": file_info["mime_type"],
        }

    def get_download_url(
        self, folder: str, filename: str, file_type: FileType, expiration: int = 3600
    ) -> Dict[str, str]:
        """Generate a presigned URL for downloading files with type validation"""
        self._validate_file_params(folder, filename, file_type)

        # Use Path for joining folder and filename
        file_path = Path(f"{folder}/{filename}")
        file_key = file_path.as_posix()

        try:
            self.client.head_object(Bucket=self.config.bucket_name, Key=file_key)
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="File not found"
                )
            raise

        url = self.generate_presigned_url(file_key, "get_object", expiration)     

        return {
            "url": url,
            "file_path": file_key,
        }


# Create a singleton instance
s3_manager = S3Manager()
