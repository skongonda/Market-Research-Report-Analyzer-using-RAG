# Use full Debian image instead of slim for better dependency support
FROM debian:bookworm

# Set environment variables for non-interactive mode
ENV DEBIAN_FRONTEND=noninteractive
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata
ENV TESSERACT_CMD=/usr/bin/tesseract
ENV POPPLER_PATH=/usr/bin

# Install Python and necessary system dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libtesseract-dev \
    ghostscript \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Verify Tesseract installation
RUN echo "Checking Tesseract installation..." && which tesseract && tesseract --version

# Install required Python packages
WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Run the application
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.
