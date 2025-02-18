from enum import Enum
from typing import Dict
from fastapi import HTTPException


class FileType(Enum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    DOCUMENT = "DOCUMENT"


class FileConfig:
    """Configuration for different file types with type-specific validation"""

    # Type-specific configurations
    CONFIGURATIONS = {
        FileType.IMAGE: {
            "extensions": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"},
            "mime_types": {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".gif": "image/gif",
                ".bmp": "image/bmp",
                ".webp": "image/webp",
                ".svg": "image/svg+xml",
            },
            "max_size": 5 * 1024 * 1024,  # 5MB
        },
        FileType.VIDEO: {
            "extensions": {".mp4", ".mov", ".avi", ".webm", ".mkv", ".m4v"},
            "mime_types": {
                ".mp4": "video/mp4",
                ".mov": "video/quicktime",
                ".avi": "video/x-msvideo",
                ".webm": "video/webm",
                ".mkv": "video/x-matroska",
                ".m4v": "video/x-m4v",
            },
            "max_size": 100 * 1024 * 1024,  # 100MB
        },
        FileType.DOCUMENT: {
            "extensions": {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt"},
            "mime_types": {
                ".pdf": "application/pdf",
                ".doc": "application/msword",
                ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                ".xls": "application/vnd.ms-excel",
                ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                ".ppt": "application/vnd.ms-powerpoint",
                ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                ".txt": "text/plain",
            },
            "max_size": 20 * 1024 * 1024,  # 20MB
        },
    }

    @classmethod
    def validate_file(cls, filename: str, file_type: FileType, file_size: int) -> Dict:
        """
        Validate file based on its type and return file information
        """
        if not filename or not file_type:
            raise HTTPException(
                status_code=400, detail="Filename and file type are required"
            )

        config = cls.CONFIGURATIONS.get(file_type)
        if not config:
            raise HTTPException(status_code=400, detail="Invalid file type")

        # Get file extension
        extension = cls._get_extension(filename)

        # Validate extension
        if extension not in config["extensions"]:
            allowed_ext = ", ".join(config["extensions"])
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file extension for {file_type.value}. Allowed: {allowed_ext}",
            )
        
        # Validate file size
        if file_size > config["max_size"]:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of {config['max_size']} bytes",
            )

        return {
            "filename": filename,
            "extension": extension,
            "mime_type": config["mime_types"].get(extension),
            "max_size": config["max_size"],
            "file_type": file_type.value,
            "file_size": file_size,
        }

    @classmethod
    def _get_extension(cls, filename: str) -> str:
        """Extract and validate file extension"""
        try:
            extension = "." + filename.rsplit(".", 1)[1].lower()
            return extension
        except IndexError:
            raise HTTPException(status_code=400, detail="File must have an extension")

    @classmethod
    def get_upload_config(cls, file_type: FileType) -> Dict:
        """Get upload configuration for a specific file type"""
        config = cls.CONFIGURATIONS.get(file_type)
        if not config:
            raise HTTPException(status_code=400, detail="Invalid file type")

        return {
            "allowed_extensions": list(config["extensions"]),
            "max_size": config["max_size"],
            "file_type": file_type.value,
        }
