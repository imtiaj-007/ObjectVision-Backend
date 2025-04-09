import cv2
from pathlib import Path
from typing import Union
from app.configuration.config import settings
from app.utils.logger import log


def process_and_convert_to_webp(
    original_image_path: Union[str, Path],
    output_dir: Union[str, Path] = None,
    quality: int = 50,
    resize_factor: float = None,
) -> str:
    """
    Processes an image by converting it to WebP format, compressing it, and optionally resizing it.

    Args:
        original_image_path (Union[str, Path]): Path to the input image.
        output_dir (Union[str, Path], optional): Directory to save the processed image. If None, saves in the same directory as the input image.
        quality (int, optional): WebP quality (0-100), default is 50.
        resize_factor (float, optional): Factor by which to resize the image. If None, only compression is applied.

    Returns:
        str: Path to the processed image.

    Raises:
        FileNotFoundError: If the image file doesn't exist.
        ValueError: If quality is not between 0 and 100 or if resize_factor is invalid.
        Exception: For other processing errors.
    """
    try:
        image_path = Path(settings.BASE_DIR, original_image_path)

        # Validate inputs
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        if not 0 <= quality <= 100:
            raise ValueError("Quality must be between 0 and 100")

        if resize_factor and resize_factor <= 0:
            raise ValueError("Resize factor must be greater than 0")

        # Create output directory if not specified
        if output_dir is None:
            output_dir = image_path.parent / "webp_processed"
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(parents=True, exist_ok=True)

        # Load the image
        img = cv2.imread(str(image_path))
        if img is None:
            raise ValueError(f"Failed to load image: {image_path}")

        # Get image dimensions
        height, width = img.shape[:2]
        base_filename = image_path.stem

        if resize_factor is not None:
            new_width = int(width * resize_factor)
            new_height = int(height * resize_factor)
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
            output_filename = f"{base_filename}_{int(resize_factor)}x.webp"
        else:
            output_filename = f"{base_filename}.webp"

        output_path = output_dir / output_filename

        # Save the image as WebP with compression
        success = cv2.imwrite(
            str(output_path),
            img,
            [cv2.IMWRITE_WEBP_QUALITY, quality],
        )

        if not success:
            raise Exception(f"Failed to save WebP image: {output_path}")

        log.success(f"Saved processed image to: {output_path}")
        
        try:
            image_path.unlink()
        except Exception as e:
            log.error(f"Failed to delete original Image: {str(e)}")
            
        return str(output_path)

    except Exception as e:
        log.error(f"Error processing image {image_path}: {str(e)}")
        raise