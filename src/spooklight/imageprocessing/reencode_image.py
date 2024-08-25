from PIL import Image
import io


def reencode_image(image_bytes: bytes, target_format: str = "PNG") -> bytes:
    """
    Re-encode the image bytes into the specified format (e.g., 'PNG' or 'JPEG').
    """
    # Load the image from the original bytes
    with io.BytesIO(image_bytes) as input_stream:
        image = Image.open(input_stream)

        # Convert to RGB if necessary (e.g., if it's 'P' mode or another mode)
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Save the image to a new bytes buffer in the target format
        with io.BytesIO() as output_stream:
            image.save(output_stream, format=target_format)
            return output_stream.getvalue()
