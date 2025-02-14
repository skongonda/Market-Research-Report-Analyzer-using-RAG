# Use full Debian for better compatibility
FROM debian:bookworm

# Set non-interactive mode to avoid prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata
ENV TESSERACT_CMD=/usr/bin/tesseract
ENV POPPLER_PATH=/usr/bin

# Install dependencies (forcing Tesseract installation)
RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libtesseract-dev \
    ghostscript \
    && rm -rf /var/lib/apt/lists/*

# Check Tesseract installation and paths
RUN echo '#!/bin/bash \n which tesseract \n tesseract --version' > /check_tesseract.sh
RUN chmod +x /check_tesseract.sh

# Set working directory
WORKDIR /app

# Copy dependencies and install them
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Ensure Tesseract and Poppler are available at runtime
CMD ["/bin/bash", "-c", "/check_tesseract.sh && uvicorn backend.app.main:app --host 0.0.0.0 --port 10000"]
