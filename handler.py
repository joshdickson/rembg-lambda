import json
import os
import time
from io import BytesIO

import boto3
from PIL import Image
from rembg import remove

# Initialize S3 client once (reused across Lambda invocations)
s3 = boto3.client('s3')

def lambda_handler(event, context):
    """
    Lambda handler for background removal.

    Expects an event dict with:
      {
        "bucket": "your-s3-bucket",
        "key": "path/to/input-image.png"
      }

    This downloads the image from S3, removes the background using rembg,
    and uploads the processed image to 'processed/<original_filename>'.

    Logs timing data for debugging and returns the output key.
    """
    start = time.time()
    bucket = event['bucket']
    key = event['key']

    # Download the input image
    t_download_start = time.time()
    img_data = BytesIO()
    s3.download_fileobj(bucket, key, img_data)
    img_data.seek(0)
    t_download_end = time.time()

    # Process the image to remove background
    t_process_start = time.time()
    input_image = Image.open(img_data).convert("RGBA")
    output_image = remove(input_image)
    t_process_end = time.time()

    # Upload the processed image to S3
    t_upload_start = time.time()
    output_buffer = BytesIO()
    output_image.save(output_buffer, format='PNG')
    output_buffer.seek(0)
    output_key = f"processed/{os.path.basename(key)}"
    s3.upload_fileobj(output_buffer, bucket, output_key, ExtraArgs={'ContentType': 'image/png'})
    t_upload_end = time.time()

    # Log timing information
    total_time = time.time() - start
    log_data = {
        "download_time": t_download_end - t_download_start,
        "process_time": t_process_end - t_process_start,
        "upload_time": t_upload_end - t_upload_start,
        "total_time": total_time
    }
    print(json.dumps(log_data))

    return {"status": "completed", "output_key": output_key}