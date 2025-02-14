# Use full Debian for better compatibility
FROM debian:bookworm

# Set non-interactive mode to avoid prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata
ENV TESSERACT_CMD=/usr/bin/tesseract
ENV POPPLER_PATH=/usr/bin

# Install dependencies (forcing Tesseract installation)
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libtesseract-dev \
    ghostscript \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python3 -m venv /opt/venv

# Activate virtual environment and install dependencies
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set working directory to /app (since your code is in backend/app)
WORKDIR /app

# Copy everything from the backend directory into /app in the container
COPY . .

COPY .env /app/.env


# Set the PYTHONPATH to include /app so Python can find your backend module
ENV PYTHONPATH="/app"

# Ensure Tesseract and Poppler are available at runtime
CMD ["/bin/bash", "-c", "ls /app && which tesseract && tesseract --version && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]


