import os
import io

import boto3
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont

from sudoku_solver.config import (
    S3_BUCKET_NAME, IMAGE_KEY, OUTPUT_DIR,
    CONTRAST_ENHANCE_FACTOR, BLUR_RADIUS, BINARIZATION_THRESHOLD
)

# ensure output dir exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

s3 = boto3.client("s3")
textract = boto3.client("textract")

def download_image_from_s3(bucket: str, key: str):
    resp = s3.get_object(Bucket=bucket, Key=key)
    data = resp["Body"].read()
    img = Image.open(io.BytesIO(data))
    return img, img.format, img.size

def preprocess_image(image: Image.Image) -> Image.Image:
    # contrast
    enhancer = ImageEnhance.Contrast(image)
    img = enhancer.enhance(CONTRAST_ENHANCE_FACTOR)
    # grayscale → blur → binarize → sharpen
    img = img.convert("L").filter(ImageFilter.GaussianBlur(BLUR_RADIUS))
    img = img.point(lambda x: 0 if x < BINARIZATION_THRESHOLD else 255, "1")
    return img.filter(ImageFilter.SHARPEN)

def extract_text_from_image(image: Image.Image):
    buf = io.BytesIO()
    image.save(buf, format="JPEG")
    resp = textract.detect_document_text(Document={"Bytes": buf.getvalue()})
    return [b for b in resp["Blocks"] if b["BlockType"] == "LINE"]

def map_text_to_grid(text_blocks, image_size, debug_img=None):
    grid = np.zeros((9,9), int)
    w, h = image_size
    draw = ImageDraw.Draw(debug_img) if debug_img else None
    font = ImageFont.load_default() if debug_img else None

    for blk in text_blocks:
        txt = blk["Text"]
        if txt.isdigit():
            bb = blk["Geometry"]["BoundingBox"]
            cx = bb["Left"] + bb["Width"]/2
            cy = bb["Top"]  + bb["Height"]/2
            col = min(int(cx*9), 8)
            row = min(int(cy*9), 8)
            grid[row, col] = int(txt)
            if draw:
                l = int(bb["Left"]*w); t = int(bb["Top"]*h)
                r = l + int(bb["Width"]*w)
                b = t + int(bb["Height"]*h)
                draw.rectangle([l,t,r,b], outline="red")
                draw.text((l,t), txt, fill="green", font=font)
    return grid

def visualize_grid(image: Image.Image) -> Image.Image:
    draw = ImageDraw.Draw(image)
    w, h = image.size
    for i in range(10):
        x = i*(w/9);    y = i*(h/9)
        draw.line([(x,0),(x,h)], fill="blue")
        draw.line([(0,y),(w,y)], fill="blue")
    return image

def process_sudoku_image(bucket=S3_BUCKET_NAME, key=IMAGE_KEY):
    img, fmt, sz = download_image_from_s3(bucket, key)
    pre = preprocess_image(img)
    blocks = extract_text_from_image(pre)
    dbg = pre.copy()
    grid = map_text_to_grid(blocks, pre.size, debug_img=dbg)
    vis = visualize_grid(dbg)
    vis.save(os.path.join(OUTPUT_DIR, "grid_output.jpg"))
    dbg.save(os.path.join(OUTPUT_DIR, "debug_output.jpg"))
    return grid, sz, fmt

def main():
    grid, size, fmt = process_sudoku_image()
    print(f"{size[0]}x{size[1]} {fmt}")
    print(grid)

if __name__ == "__main__":
    main()
