import os
import hashlib
import hmac
import base64
from pathlib import Path
from urllib.parse import quote

import aiofiles
from io import BytesIO
from PIL import Image, ImageFile

from typing import Dict, Optional, Union
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Depends, status
from fastapi.security import APIKeyHeader

from app.configuration.config import settings
from app.services.s3_bucket_service import s3_manager
from app.schemas.enums import ImageFormatsEnum, FileType
from app.helpers.file_types import FileConfig
from app.utils.logger import log


api_key_header = APIKeyHeader(name="X-API-Key")
ImageFile.LOAD_TRUNCATED_IMAGES = True 


def verify_api_key(api_key: str = Depends(api_key_header)) -> str:
    """Verify the API key provided in the request header."""
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )
    return api_key


def is_path_allowed(file_path: Union[str, Path]) -> bool:
    """Check if the requested file path is within the base directory and one of the public folders."""
    normalized_path = Path(file_path).resolve()

    # Prevent path traversal attacks
    if ".." in normalized_path.parts:
        return False

    base_path = Path(settings.BASE_DIR).resolve()
    try:
        if not normalized_path.is_relative_to(base_path):
            return False
    except AttributeError:  # Compatibility for Python < 3.9
        if not str(normalized_path).startswith(str(base_path)):
            return False

    # Check if the file is within a public folder
    for folder in settings.PUBLIC_FOLDERS:
        folder_path = base_path / folder
        try:
            if normalized_path.is_relative_to(folder_path.resolve()):
                return True
        except AttributeError:
            if str(normalized_path).startswith(str(folder_path.resolve())):
                return True

    return False


def file_exists(file_path: Union[Path, str]) -> bool:
    """Check if the file exists and is readable."""
    full_path = Path(settings.BASE_DIR) / file_path
    return full_path.is_file() and os.access(full_path, os.R_OK)


def generate_signature(file_path: str, expires_at: int) -> str:
    """Generate a signature for the file path and expiry time using HMAC-SHA256."""
    message = f"{file_path}:{expires_at}".encode()
    signature = hmac.new(settings.SECRET_KEY.encode(), message, hashlib.sha256).digest()

    return base64.urlsafe_b64encode(signature).rstrip(b"=").decode()


def generate_presigned_url(
    file_path: Path, expiry_minutes: Optional[int] = None
) -> Dict:
    """Generate a pre-signed URL for the given file path."""
    if expiry_minutes is None:
        expiry_minutes = settings.TOKEN_EXPIRY

    expires_at = int(
        (datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes)).timestamp()
    )

    signature = generate_signature(file_path, expires_at)

    encoded_file_path = quote(file_path, safe="")
    url = f"{settings.API_BASE_URL}/files/local/{encoded_file_path}?signature={signature}&expires={expires_at}"

    return {
        "url": url,
        "expires_at": datetime.fromtimestamp(expires_at, tz=timezone.utc),
    }


async def convert_file_format(
    file_path: Union[Path, str], file_extension: ImageFormatsEnum
):
    try:
        with open(file_path, "rb") as file:
            image_bytes = file.read()

        with Image.open(BytesIO(image_bytes)) as image:
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")

            # Convert to file to specified extension
            img_buffer = BytesIO()
            image.save(img_buffer, format=file_extension.value.upper(), quality=75)
            img_buffer.seek(0)

        # Generate a unique filename
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename_without_extension = Path(file_path).stem
        unique_filename = f"{timestamp}_{filename_without_extension}.{file_extension.value}"

        storage_path = Path(settings.BASE_DIR) / "cache/image" / unique_filename
        storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Save the file in image cache
        async with aiofiles.open(storage_path, "wb") as buffer:
            await buffer.write(img_buffer.getvalue())

        return storage_path

    except Exception as e:
        log.error(f"Error in convert_file_format: {str(e)}")
        raise


def upload_processed_image(
    local_file_path: Union[Path, str],
    destination_folder: str,
    file_type: FileType = FileType.IMAGE,
):
    """
    Upload a processed image from local server to S3

    Parameters:
    - local_file_path: Path to the file on your local server
    - destination_folder: S3 folder to upload to
    - file_type: Type of file (default: IMAGE)

    Returns:
    - S3 file key for the uploaded file
    """
    # Check if file exists
    file_path = Path(local_file_path)    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {local_file_path}")

    # Build the S3 key using our existing method
    filename = file_path.name    
    file_key = s3_manager._build_file_key(destination_folder, filename)

    # Determine content type based on file extension
    ext = file_path.suffix.lower()
    file_config = FileConfig.CONFIGURATIONS.get(file_type)
    content_type = file_config["mime_types"].get(ext)

    try:
        s3_manager.client.upload_file(
            Filename=str(file_path),
            Bucket=s3_manager.config.bucket_name,
            Key=file_key,
            ExtraArgs={"ContentType": content_type}
        )        
        log.info(f"Successfully uploaded {filename} to S3 at {file_key}")                
        return file_key

    except Exception as e:
        log.error(f"Failed to upload {filename} to S3: {str(e)}")
        raise
