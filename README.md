# rembg-lambda

A serverless image background removal service that runs on AWS Lambda using the `rembg` library and the `u2net` model. This setup ensures the model is pre-downloaded during the Docker build stage, minimizing cold start overhead and enabling quick, on-demand background removal from images stored in Amazon S3.

## Features

- **On-Demand Execution:** Pay only for what you use. Lambda scales seamlessly with load.
- **Pre-Downloaded Model:** The `u2net` model is fetched at build time, reducing latency on first invocation.
- **Minimal Dependencies:** Uses `rembg` for background removal, `boto3` for S3 I/O, and Pillow for image manipulation.

## Getting Started

### Prerequisites

- Docker installed locally.
- AWS CLI configured with credentials that have permission to update a Lambda function and access S3.
- An existing S3 bucket to store input images and receive processed outputs.
- An existing Lambda function configured to use an image from ECR.

### Building the Image

```bash
docker build -t rembg-lambda .
```

### Tagging and Pushing to ECR

Assuming you have an ECR repository named rembg-lambda:

```bash
ACCOUNT_ID=123456789012
REGION=us-east-1
IMAGE_URI="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/rembg-lambda:latest"

docker tag rembg-lambda:latest $IMAGE_URI
docker push $IMAGE_URI
```

### Updating the Lambda Function

Replace YourLambdaFunctionName and make sure the Lambda execution role has permission to access your S3 bucket.

```bash
aws lambda update-function-code \
  --function-name YourLambdaFunctionName \
  --image-uri $IMAGE_URI \
  --region $REGION
```

### Testing the Function

Use test_event.json as a sample invocation event, adjusting the bucket and key as needed.

```bash
aws lambda invoke \
  --function-name YourLambdaFunctionName \
  --payload file://test_event.json \
  --cli-binary-format raw-in-base64-out \
  response.json
```

Check response.json to see the function’s output. The processed image will appear under processed/ in your S3 bucket.

### Customization

- Adjust environment variables in the Dockerfile if you need different caching behavior or want to disable Numba JIT.
- Modify handler.py to support different image formats or output naming schemes.
- Update requirements.txt if you add or remove dependencies.
