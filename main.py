from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from typing import Optional
import os

# Library imports
import cv2
import paddle
from img2table.ocr import PaddleOCR
import numpy as np
import pandas as pd
from img2table.document import Image
from tempfile import NamedTemporaryFile
from fastapi.responses import HTMLResponse

app = FastAPI()

# Define request model
class ImageUpload(BaseModel):
    image: UploadFile

# Preprocessing method
def Preprocessing(image_path):
    # Resize the image to 100% of the original size
    resize_factor = 1
    # Check if the image file exists
    if os.path.exists(image_path):
        # Get the size of the image file in bytes
        size_bytes = os.path.getsize(image_path)

        # Convert the size from bytes to megabytes
        size_mb = size_bytes / (1024 * 1024)  # 1 MB = 1024 * 1024 bytes

        if size_mb >= 5:
            # Resize the image to 6% of the original size
            resize_factor = 0.06
        elif size_mb >= 4:
            # Resize the image to 7.5% of the original size
            resize_factor = 0.075
        elif size_mb >= 3:
            # Resize the image to 10% of the original size
            resize_factor = 0.1
        elif size_mb >= 2:
            # Resize the image to 15% of the original size
            resize_factor = 0.07
        elif size_mb >= 1:
            # Resize the image to 30% of the original size
            resize_factor = 0.3
        elif size_mb >= 0.5:
            # Resize the image to 60% of the original size
            resize_factor = 0.6
        elif size_mb >= 0.3:
            # Resize the image to 20% of the original size
            resize_factor = 0.2

        # Load the image
        image = cv2.imread(image_path)

        # Get the original dimensions
        original_height, original_width = image.shape[:2]

        # Calculate new dimensions based on the resize factor
        new_width = int(original_width * resize_factor)
        new_height = int(original_height * resize_factor)

        # Resize the image
        resized_image = cv2.resize(image, (new_width, new_height))

        # Save the resized image
        cv2.imwrite(image_path, resized_image)

# Image_To_Table_OCR method
def Image_To_Table_OCR(Image_array):
    #Preprocessing(image_path)
    # Convert image to Array
    #Image_array = Image(image_path)
    # Define OCR
    ocr = PaddleOCR(lang="en")
    # Convert Image Array to Excel file, in dest give the absolute path of excel file
    Image_array.to_xlsx(dest='table.xlsx',
                       ocr=ocr,
                       implicit_rows=False,
                       borderless_tables=False,
                       min_confidence=10)

    # Read excel file
    excel_file_path = 'table.xlsx'

    # Convert excel into pandas dataframe
    dataframe = pd.read_excel(excel_file_path)

    # Convert dataframe into JSON
    return dataframe.to_json(orient='records')

def read_imagefile(file):
    image = Image(file)
    return image



@app.post("/uploadfiles/")
async def predict_api(file: UploadFile = File(...)):
    extension = file.filename.split(".")[-1] in ("jpg", "jpeg", "png")
    if not extension:
        return "Image must be jpg or png format!"
    image = read_imagefile(await file.read())
    prediction = Image_To_Table_OCR(image)

    return prediction







