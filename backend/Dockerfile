FROM python:3.11-slim

# Install necessary packages
RUN apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-eng poppler-utils libtesseract-dev ghostscript

# Set environment variables (adjust according to your needs)
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata/
ENV POPPLER_PATH=/usr/bin/pdftoppm

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

# Copy your app files
COPY backend /app
WORKDIR /app

# Command to run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
