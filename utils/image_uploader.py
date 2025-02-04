import base64
import os
from PIL import Image
import io

MAX_FILE_SIZE_MB = 2


def compress_image(image_path, max_size_kb=300, quality=50):
    try:
        image = Image.open(image_path)
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        output_io = io.BytesIO()
        image.save(output_io, format="JPEG", quality=quality)
        output_io.seek(0)  # Reset buffer

        compressed_data = output_io.getvalue()
        if len(compressed_data) > max_size_kb * 1024:
            raise ValueError("Compressed image is still too large. Please choose a smaller image.")

        return compressed_data
    except Exception as e:
        print(f"Error compressing image: {str(e)}")
        return None


def file_to_base64(file_path, is_image=True):
    try:
        if is_image:
            compressed_data = compress_image(file_path)
            if compressed_data is None:
                return None
            return base64.b64encode(compressed_data).decode("utf-8")
        else:
            with open(file_path, "rb") as file:
                return base64.b64encode(file.read()).decode("utf-8")
    except Exception as e:
        print(f"Error converting file to Base64: {str(e)}")
        return None


