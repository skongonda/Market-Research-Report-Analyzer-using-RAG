FROM python:3.11-slim

# Install necessary system dependencies
RUN apt-get update && \
    apt-get install -y tesseract-ocr tesseract-ocr-eng libtesseract-dev poppler-utils ghostscript

# Install Tesseract
RUN apt-get update && apt-get install -y tesseract-ocr

# Set environment variables for Tesseract and Poppler
ENV TESSDATA_PREFIX="/usr/share/tesseract-ocr/5/tessdata"
ENV POPPLER_PATH="/usr/bin/pdftoppm"
ENV TESSERACT_CMD="/usr/bin/tesseract"

# Copy the requirements file to install Python dependencies
COPY backend/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the application files into the container
COPY backend /app
WORKDIR /app

# Expose the port (this is required for Render)
EXPOSE 10000

# Command to run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
