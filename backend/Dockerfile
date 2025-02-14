# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata
ENV TESSERACT_CMD=/usr/bin/tesseract
ENV POPPLER_PATH=/usr/bin

# Install system dependencies and Tesseract OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libtesseract-dev \
    ghostscript \
    && rm -rf /var/lib/apt/lists/*

# Verify that Tesseract is installed
RUN echo "Checking Tesseract installation..." && which tesseract && tesseract --version

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code
COPY . .

# Run the application
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "10000"]
