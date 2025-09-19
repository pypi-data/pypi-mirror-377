from PIL import Image

def resize_image(image_path, output_path, size):
    image = Image.open(image_path)
    resized = image.resize(size)
    resized.save(output_path)

def rotate_image(image_path, output_path, degrees):
    image = Image.open(image_path)
    rotated = image.rotate(degrees)
    rotated.save(output_path)
