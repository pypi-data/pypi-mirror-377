from PIL import Image, ImageFilter

def apply_blur(image_path, output_path):
    image = Image.open(image_path)
    blurred = image.filter(ImageFilter.BLUR)
    blurred.save(output_path)

def apply_contour(image_path, output_path):
    image = Image.open(image_path)
    contoured = image.filter(ImageFilter.CONTOUR)
    contoured.save(output_path)
