#!/bin/bash
# Install Tesseract and Poppler
apt-get update
apt-get install -y tesseract-ocr poppler-utils

# Start the FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port $PORT
