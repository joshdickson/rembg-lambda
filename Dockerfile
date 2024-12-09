FROM public.ecr.aws/lambda/python:3.9

# Set environment variables for caching and models
ENV HOME=/tmp
ENV XDG_CACHE_HOME=/tmp
ENV U2NET_HOME=/var/task/.u2net
ENV POOCH_CACHE_DIR=/var/task/pooch
ENV NUMBA_CACHE_DIR=/tmp/numba_cache

# If caching or parallelization causes issues, consider disabling JIT:
# ENV NUMBA_DISABLE_JIT=1

# Install necessary tools and Python packages
RUN yum install -y wget && yum clean all

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create directories for model and cache
RUN mkdir -p /var/task/.u2net /var/task/pooch /tmp/numba_cache

# Download a dummy image to trigger model download at build time
RUN wget https://raw.githubusercontent.com/danielgatis/rembg/master/examples/car-1.jpg -O /var/task/dummy.jpg

# Force model download at build time by processing a dummy image
RUN rembg i /var/task/dummy.jpg /var/task/dummy.out.png

# Ensure model files are world-readable
RUN chmod -R a+r /var/task/.u2net

# Copy the handler code into the Lambda task root
COPY handler.py ${LAMBDA_TASK_ROOT}

# Set the Lambda function entry point
CMD ["handler.lambda_handler"]