from PIL import Image
import pytesseract

/usr/share/tesseract-ocr/4.00/tessdata

print(pytesseract.image_to_string(Image.open('test.png')))