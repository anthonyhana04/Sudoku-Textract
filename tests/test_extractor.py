import pytest
from PIL import Image
from sudoku_solver.extractor import preprocess_image, map_text_to_grid

def test_preprocess_image_mode_and_size():
    img = Image.new("RGB", (90,90), "white")
    out = preprocess_image(img)
    assert out.mode == "1"
    assert out.size == (90,90)

def test_map_text_to_grid_simple():
    # simulate one digit in top-left cell
    blocks = [{
        "BlockType": "LINE",
        "Text": "7",
        "Geometry": {
            "BoundingBox": {"Left": 0.02, "Top": 0.02, "Width": 0.05, "Height": 0.05}
        }
    }]
    grid = map_text_to_grid(blocks, (900,900))
    assert grid[0,0] == 7
