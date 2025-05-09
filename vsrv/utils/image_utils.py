'''
    Image Utils
'''
import base64
import os
from io import BytesIO
from PIL import Image
from vsrv.exceptions import ApplicationException, ExceptionReason, ExceptionSeverity
from vsrv.logging.insight import SystemInsight


class ImageUtils:
    '''
        Image Utils 
    '''
    @staticmethod
    def process_save_image(log_msg_heading: str, base64_string: str | None, static_path: str, image_name: str):
        '''
        Process and Save Image 
        '''
        img_data: bytes | None = None
        if base64_string is None:
            raise ApplicationException(
                message="Invalid Base64 string",
                severity=ExceptionSeverity.CRITICAL,
                reason=ExceptionReason.USER
            )

        try:
            # Decode the base64 string
            img_data = base64.b64decode(base64_string)
        except Exception as exc:
            raise ApplicationException(
                message="Invalid Base64 string",
                severity=ExceptionSeverity.CRITICAL,
                reason=ExceptionReason.USER
            ) from exc

        # Validate the image size (300 KB max)
        max_size_bytes = 300 * 1024  # 300 KB
        if len(img_data) > max_size_bytes:
            raise ApplicationException(
                message=f"Image size exceeds 300 KB (current size: {len(img_data)} bytes)",
                severity=ExceptionSeverity.CRITICAL,
                reason=ExceptionReason.USER
            )

        try:
            # Open the image using PIL
            img = Image.open(BytesIO(img_data))
        except Exception as exc:
            raise ApplicationException(
                message="Unable to open image data",
                severity=ExceptionSeverity.CRITICAL,
                reason=ExceptionReason.SYSTEM
            ) from exc

        if not os.path.exists(static_path):
            os.makedirs(static_path)

        # Determine the format (PNG or JPG)
        format_ext = "JPEG"
        ext = "jpg"

        # Generate a unique filename
        filename = f"{image_name}.{ext}"
        filepath = os.path.join(static_path, filename)

        try:
            # Save the image
            img.save(filepath, format=format_ext)
            log_msg = f'{log_msg_heading} : Image Saved {filepath}'
            SystemInsight.logger().info(msg=log_msg)
        except Exception as exc:
            raise ApplicationException(
                message="Unable to save image",
                severity=ExceptionSeverity.CRITICAL,
                reason=ExceptionReason.SYSTEM
            ) from exc

        return filepath
