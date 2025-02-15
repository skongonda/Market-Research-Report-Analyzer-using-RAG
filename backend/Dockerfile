# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install system dependencies including Tesseract and Poppler
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \  
    tesseract-ocr-eng \
    libgl1 \
    libsm6 \
    libxext6 \
    libjpeg-dev \
    zlib1g-dev \
    libtiff5-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Verify Tesseract installation and log the correct path
RUN which tesseract && tesseract --version

# Add Explicit PATH Configuration
ENV POPPLER_PATH=/usr/bin
ENV TESSERACT_CMD=/usr/bin/tesseract
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
# ENV PATH="/usr/bin:${PATH}"

# Set the working directory
WORKDIR /app

# Copy the requirements.txt first (to leverage Docker's cache mechanism)
COPY backend/requirements.txt .

# Install Python dependencies
# RUN pip install --upgrade pip && \
#     pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# COPY backend/ /app

# Copy the rest of the application code to the container
COPY backend/ .

# Expose the port for the application
EXPOSE 10000

# Start the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]