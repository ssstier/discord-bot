from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import io


def extract_text(image_data: bytes):
    image = Image.open(io.BytesIO(image_data))
    image = image.convert('L')  # Convert to grayscale
    image = image.filter(ImageFilter.SHARPEN)  # Apply sharpen filter
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)  # Increase contrast
    text = pytesseract.image_to_string(image)

    if len(text) == 0:
        return "No text found."
    else:
        return text
