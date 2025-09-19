import numpy as np
from PIL import Image

def image_to_array(image_path):
    image = Image.open(image_path)
    return np.array(image)

def array_to_image(array, output_path):
    image = Image.fromarray(array)
    image.save(output_path)
