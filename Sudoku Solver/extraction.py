import boto3
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import io
import os

S3_BUCKET_NAME = "sudoku-picture-bucket"
IMAGE_KEY = "Puzzle1.JPG"
OUTPUT_DIR = "output" 

import os
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

s3 = boto3.client('s3')
textract = boto3.client('textract')

# Download the image from S3 Bucket
def download_image_from_s3(bucket_name, image_key):
    response = s3.get_object(Bucket=bucket_name, Key=image_key)
    image_data = response['Body'].read()
    image = Image.open(io.BytesIO(image_data))
    image_format = image.format  # Get image format (JPG, PNG, etc.)
    image_size = image.size  # Get image dimensions (width, height)
    return image, image_format, image_size


# Pre-process the image
def preprocess_image(image):
    # Increase contrast
    enhancer = ImageEnhance.Contrast(image)
    enhanced_image = enhancer.enhance(4.0) # around 4.0 seems to work well
    
    # Convert to grayscale
    gray_image = enhanced_image.convert('L')
    
    # Apply Gaussian blur to reduce noise
    blurred_image = gray_image.filter(ImageFilter.GaussianBlur(1)) # never change
    
    # Binarize with a different threshold
    binarized_image = blurred_image.point(lambda x: 0 if x < 135 else 255, '1') # found that 135 - 150 is sweet spot
    
    # Sharpen the image
    sharpened_image = binarized_image.filter(ImageFilter.SHARPEN)
    
    return sharpened_image

# Use Textract to extract text
def extract_text_from_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    response = textract.detect_document_text(Document={'Bytes': buffered.getvalue()})
    text_blocks = [block for block in response['Blocks'] if block['BlockType'] == 'LINE']
    return text_blocks

# Map extracted text to Sudoku grid
def map_text_to_grid(text_blocks, image_size, debug_image=None):
    sudoku_grid = np.zeros((9, 9), dtype=int)
    
    img_width, img_height = image_size
    
    cell_width = img_width / 9
    cell_height = img_height / 9
    
    # Debug image draw
    draw = ImageDraw.Draw(debug_image) if debug_image else None
    font = ImageFont.load_default() if debug_image else None
    
    for block in text_blocks:
        bbox = block['Geometry']['BoundingBox']
        text = block['Text']
        
        if text.isdigit():
            # Calculate approximate grid cell by the center of the bounding box
            center_x = bbox['Left'] + bbox['Width'] / 2
            center_y = bbox['Top'] + bbox['Height'] / 2
            
            col = int(center_x * 9)
            row = int(center_y * 9)
            
            # Ensure row and column are within bounds
            row = max(0, min(row, 8))
            col = max(0, min(col, 8))
            
            sudoku_grid[row, col] = int(text)
            
            # Draw bounding box and text for debugging
            if debug_image:
                left = int(bbox['Left'] * img_width)
                top = int(bbox['Top'] * img_height)
                right = left + int(bbox['Width'] * img_width)
                bottom = top + int(bbox['Height'] * img_height)
                draw.rectangle([left, top, right, bottom], outline="red")
                draw.text((left, top), text, fill="green", font=font)
    
    return sudoku_grid

# Visualize grid for debugging
def visualize_grid(image):
    draw = ImageDraw.Draw(image)
    width, height = image.size
    cell_width = width / 9
    cell_height = height / 9
    
    for i in range(10):
        x = i * cell_width # Vert Lines
        draw.line([(x, 0), (x, height)], fill="blue")
        y = i * cell_height # Horizontal
        draw.line([(0, y), (width, y)], fill="blue")
    
    return image

# Complete processing function
def process_sudoku_image(bucket_name, image_key):
    image, image_format, image_size = download_image_from_s3(bucket_name, image_key)
    preprocessed_image = preprocess_image(image)
    text_blocks = extract_text_from_image(preprocessed_image)
    
    debug_image = preprocessed_image.copy()
    sudoku_grid = map_text_to_grid(text_blocks, preprocessed_image.size, debug_image)
    
    # Visualize grid for debugging
    grid_image = visualize_grid(debug_image)
    grid_image.save(os.path.join(OUTPUT_DIR, "grid_output.jpg"))
    debug_image.save(os.path.join(OUTPUT_DIR, "debug_output.jpg"))
    
    return sudoku_grid, image_size, image_format

# Run the processing
sudoku_grid, image_size, image_format = process_sudoku_image(S3_BUCKET_NAME, IMAGE_KEY)
print("AWS Textract")
print(f"{image_size[0]}x{image_size[1]} {image_format}")
print(sudoku_grid, '\n')

