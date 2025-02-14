# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install system dependencies including Tesseract and Poppler
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libleptonica-dev \
    poppler-utils \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Verify Tesseract installation and log the correct path
RUN which tesseract && tesseract --version

# Set the working directory
WORKDIR /app

# Copy the requirements.txt first (to leverage Docker's cache mechanism)
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY . .

# Expose the port for the application
EXPOSE 10000

# Start the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]