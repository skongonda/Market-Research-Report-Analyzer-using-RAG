FROM debian:bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata
ENV TESSERACT_CMD=/usr/bin/tesseract
ENV POPPLER_PATH=/usr/bin

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    tesseract-ocr tesseract-ocr-eng poppler-utils libtesseract-dev \
    ghostscript && rm -rf /var/lib/apt/lists/*

# Create a virtual environment
RUN python3 -m venv /opt/venv

# Activate virtual environment and install Python dependencies
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set the working directory to /app and copy the code
WORKDIR /app
COPY . .

# Ensure Tesseract and Poppler are available and run the FastAPI app
CMD ["/bin/bash", "-c", "which tesseract && tesseract --version && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
