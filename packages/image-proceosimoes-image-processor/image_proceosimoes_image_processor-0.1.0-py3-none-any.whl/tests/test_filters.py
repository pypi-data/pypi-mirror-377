import os
from image_processor import filters

def test_apply_blur(tmp_path):
    input_img = tmp_path / "input.png"
    output_img = tmp_path / "output.png"
    from PIL import Image
    Image.new("RGB", (10, 10), color="red").save(input_img)

    filters.apply_blur(str(input_img), str(output_img))
    assert os.path.exists(output_img)
