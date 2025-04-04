import hmac
from pathlib import Path
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse
from app.configuration.config import settings
from app.services.auth_service import AuthService
from app.services.file_service import (
    verify_api_key,
    is_path_allowed,
    generate_signature,
    generate_presigned_url,
    convert_file_format
)
from app.schemas.general_schema import PresignedUrlRequest, PresignedUrlResponse
from app.schemas.enums import FileType, ImageFormatsEnum
from app.utils.logger import log

router = APIRouter()


@router.post(
    "/local/generate-presigned-url",
    response_model=PresignedUrlResponse,
    dependencies=[Depends(verify_api_key), Depends(AuthService.authenticate_user)],
)
async def create_presigned_url(request: PresignedUrlRequest):
    """Generate a presigned URL for accessing a specific file."""
    try:
        file_path = request.file_path
        file_url = Path(request.file_path).as_posix()

        if not is_path_allowed(file_path):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this path is not allowed",
            )

        presigned_data = generate_presigned_url(file_url, request.expiry_minutes)
        return {
            **presigned_data,
            "file_path": file_path
        }
    
    except Exception as e:
        log.error(f"Error in create_presigned_url: {str(e)}")


@router.get(
    "/local/{file_path:path}",
)
async def get_file(
    file_path: str, 
    signature: str = Query(...), 
    expires: int = Query(...)
):
    """Serve a file using the presigned URL."""
    try:
        # Check if URL has expired
        current_time = int(datetime.now(timezone.utc).timestamp())
        if current_time > expires:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="URL has expired"
            )

        # Verify signature
        normalized_path = Path(file_path.lstrip("/"))
        expected_signature = generate_signature(normalized_path.as_posix(), expires)
        if not hmac.compare_digest(signature, expected_signature):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid signature"
            )

        # Check if path is allowed
        if not is_path_allowed(str(normalized_path)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this path is not allowed",
            )

        full_path = (Path(settings.BASE_DIR) / file_path.lstrip("/")).resolve()

        # Ensure the file exists and is a valid file
        if not full_path.exists() or not full_path.is_file():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
            )

        return FileResponse(full_path, media_type="application/octet-stream")

    except Exception as e:
        log.error(f"Error in get_file: {str(e)}")
        raise


@router.get(
    "/download/{file_path:path}",
)
async def download_file(
    file_path: str, 
    file_type: FileType = Query(...), 
    file_extension: ImageFormatsEnum = Query(...)
):
    """Serve a file using the presigned URL of specified format."""
    try:
        # Check if path is allowed
        normalized_path = Path(file_path.lstrip("/"))

        if not is_path_allowed(str(normalized_path)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this path is not allowed",
            )

        full_path = (Path(settings.BASE_DIR) / file_path.lstrip("/")).resolve()

        # Ensure the file exists and is a valid file
        if not full_path.exists() or not full_path.is_file():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
            )

        if file_extension != ImageFormatsEnum.WEBP:
            full_path = await convert_file_format(full_path, file_extension)

        media_type = f"image/{file_extension.value}"
        return FileResponse(full_path, media_type=media_type)

    except Exception as e:
        log.error(f"Error in get_file: {str(e)}")
        raise