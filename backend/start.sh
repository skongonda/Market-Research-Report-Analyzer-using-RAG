#!/bin/bash
# ----- Add these lines -----
sudo apt-get update
sudo apt-get install -y tesseract-ocr poppler-utils
# ---------------------------
uvicorn app.main:app --host 0.0.0.0 --port $PORT
