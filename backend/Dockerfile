FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    software-properties-common \
    tesseract-ocr \
    tesseract-ocr-eng \
    libtesseract-dev \
    poppler-utils \
    ghostscript \
    && rm -rf /var/lib/apt/lists/*

# Verify Tesseract installation
RUN echo "Checking Tesseract installation..." \
    && which tesseract \
    && tesseract --version

# Set environment variables
ENV TESSERACT_CMD=/usr/bin/tesseract
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata
ENV POPPLER_PATH=/usr/bin

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "10000"]
