import os
from datetime import datetime
import pytesseract
from PIL import Image, ImageEnhance, ImageOps
import numpy as np

SETTINGS = {
    'brightness': 1.0,
    'threshold': 128,
    'invert_colors': False,
    'ascii_chars': '█▓▒░ ',
    'output_folder': 'asciioutput'
}

# OCR ile metinleri koordinatlarıyla çıkar
def ocr_extract_boxes(image):
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    boxes = []
    for i, text in enumerate(data['text']):
        if text.strip():
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            boxes.append((text, (x, y, x + w, y + h)))
    return boxes

# Görüntüyü ASCII'ye dönüştür
def image_to_ascii(image, ascii_chars, new_width=100):
    width, height = image.size
    aspect_ratio = height / width
    new_height = int(aspect_ratio * new_width * 0.55)
    image = image.resize((new_width, new_height))

    pixels = np.array(image)
    chars = np.asarray(list(ascii_chars))

    normalized_pixels = (pixels - pixels.min()) / np.ptp(pixels)
    indices = (normalized_pixels * (len(chars) - 1)).astype(int)
    ascii_image = ["".join(row) for row in chars[indices]]

    return ascii_image

# Metinleri ASCII üzerine yerleştir
def overlay_text(ascii_image, boxes, original_size, ascii_size):
    ratio_x = ascii_size[0] / original_size[0]
    ratio_y = ascii_size[1] / original_size[1]

    for text, (x1, y1, x2, y2) in boxes:
        ascii_x = int(x1 * ratio_x)
        ascii_y = int(y1 * ratio_y * 0.55)
        if ascii_y < len(ascii_image):
            line = ascii_image[ascii_y]
            text_len = min(len(text), len(line) - ascii_x)
            ascii_image[ascii_y] = line[:ascii_x] + text[:text_len] + line[ascii_x + text_len:]

    return ascii_image

# Ana dönüştürme fonksiyonu
def convert_image_to_ascii_ocr(image_path, settings):
    image = Image.open(image_path).convert('L')

    if settings['invert_colors']:
        image = ImageOps.invert(image)

    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(settings['brightness'])

    image = image.point(lambda p: p > settings['threshold'] and 255)

    original_size = image.size

    boxes = ocr_extract_boxes(image)
    ascii_art = image_to_ascii(image, settings['ascii_chars'])
    ascii_size = (100, len(ascii_art))

    combined_ascii = overlay_text(ascii_art, boxes, original_size, ascii_size)

    output = f"## Birleştirilmiş OCR ve ASCII Çıktısı:\n````\n{''.join(combined_ascii)}\n````"

    if not os.path.exists(settings['output_folder']):
        os.makedirs(settings['output_folder'])

    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = os.path.join(settings['output_folder'], f'{timestamp}.md')

    with open(filename, 'w', encoding='utf-8') as file:
        file.write(output)

    print(f"Sonuç başarıyla kaydedildi: {filename}")

# Test için örnek kullanım
if __name__ == "__main__":
    test_image = "test.png"
    convert_image_to_ascii_ocr(test_image, SETTINGS)
