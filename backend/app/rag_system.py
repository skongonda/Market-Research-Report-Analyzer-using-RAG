TABLE_SEPARATOR = "---TABLE_CONTENT---"

from openai import OpenAI
import numpy as np
from scipy.spatial.distance import cosine
from app.utils import load_environment, with_retry
import os
import pdfplumber
from pdf2image import convert_from_bytes
import pytesseract
import logging
import subprocess
import traceback
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class RAGSystem:
    def __init__(self):
        self.api_key = load_environment()
        self.client = OpenAI(api_key=self.api_key)
        self.table_separator = "=== TABLE ==="
        
        # Use environment variables with Linux defaults
        self.poppler_path = os.getenv('POPPLER_PATH', '/usr/bin')
        self.tesseract_cmd = os.getenv('TESSERACT_CMD', '/usr/bin/tesseract')
        self.tessdata_dir = os.getenv('TESSDATA_PREFIX', '/usr/share/tesseract-ocr/5/tessdata')
        
        # Configure Tesseract
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
        os.environ['TESSDATA_PREFIX'] = self.tessdata_dir


    def _configure_tesseract(self):
        try:
            tesseract_version = subprocess.run([self.tesseract_path, '--version'], check=True, capture_output=True)
            print("Tesseract version:", tesseract_version.stdout.decode())
        except Exception as e:
            print("Error during Tesseract configuration:", e)
            raise e

    def extract_text_from_pdf(self, file_path, max_pages=5):
        text = ""
        try:
            logging.info(f"Processing {file_path} with standard extraction")
            # First attempt: Standard text extraction
            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages[:max_pages]):
                    page_text = page.extract_text() or ""
                    if page_text:
                        text += f"\nPAGE {i+1} TEXT:\n{page_text}"
                        logging.info(f"Extracted text from page {i+1}")

            # OCR fallback with improved error handling
            if not text.strip():
                logging.warning("No text found via standard extraction. Attempting OCR")
                with open(file_path, "rb") as f:
                    try:
                        images = convert_from_bytes(
                            f.read(),
                            first_page=1,
                            last_page=max_pages,
                            poppler_path=self.poppler_path,
                            dpi=300
                        )
                        logging.info(f"Converted {len(images)} pages to images")
                        text = "\n".join([
                            pytesseract.image_to_string(
                                img,
                                config=f'--tessdata-dir "{self.tessdata_dir}" --psm 3 --oem 3'
                            ) for img in images
                        ])
                        if text.strip():
                            logging.info("OCR extraction successful")
                    except Exception as ocr_error:
                        logging.error(f"OCR failed: {traceback.format_exc()}")
                        return ""

            return text
        except Exception as e:
            logging.error(f"PDF Processing Error: {traceback.format_exc()}")
            return ""
        
    def chunk_text(self, text, max_tokens=1000):
        """Split text into chunks of max_tokens"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_tokens = 0

        for word in words:
            current_chunk.append(word)
            current_tokens += 1
            if current_tokens >= max_tokens:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_tokens = 0

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def _validate_content(self, text):
        """Check if the extracted text is meaningful."""
        words = [w for w in text.split() if len(w) > 3]
        return len(words) > 50  # Require at least 50 meaningful words

    def get_embedding(self, text):
        """Generate embedding for text."""
        try:
            clean_text = text.replace("\n", " ").replace("  ", " ").strip()
            if len(clean_text) > 8000:
                clean_text = clean_text[:8000]
            
            if not clean_text:
                return np.zeros(1536)
            
            response = with_retry(lambda: self.client.embeddings.create(
                input=[clean_text],
                model="text-embedding-3-small"
            ))
            return np.array(response.data[0].embedding)
        except Exception as e:
            print(f"Embedding Error: {str(e)}")
            return np.zeros(1536)

    def query(self, query_text, file_paths):
        """Process user query and generate a response."""
        try:
            if not file_paths:
                logging.error("No files provided for query")
                return "Error: No documents provided"

            all_chunks = []
            for file_path in file_paths:
                if not os.path.exists(file_path):
                    logging.error(f"File not found: {file_path}")
                    continue
                
                text = self.extract_text_from_pdf(file_path)
                if not text:
                    logging.warning(f"No text extracted from {file_path}")
                    continue
                
                # Validate minimum content
                if not self._validate_content(text):
                    logging.warning(f"Insignificant content in {file_path}")
                    continue
                
                chunks = self.chunk_text(text)
                logging.info(f"Created {len(chunks)} chunks from {file_path}")
                
                for chunk in chunks:
                    embedding = self.get_embedding(chunk)
                    all_chunks.append((chunk, embedding, file_path))

            if not all_chunks:
                return "Error: No analyzable content found in documents"

            query_embedding = self.get_embedding(query_text)
            results = []
            for chunk, emb, path in all_chunks:
                similarity = 1 - cosine(query_embedding, emb)
                results.append((similarity, chunk, path))

            results.sort(reverse=True, key=lambda x: x[0])
            top_chunks = results[:5]

            context = []
            for score, chunk, path in top_chunks:
                source = f"From {path.split('/')[-1]}"
                if self.table_separator in chunk:
                    context.append(f"TABLE DATA ({source}):\n{chunk.split(self.table_separator)[-1]}")
                else:
                    context.append(f"TEXT CONTENT ({source}):\n{chunk}")

            context_string = "\n\n".join([f"### Context {i+1}:\n{c}" for i, c in enumerate(context)])
            prompt = (
                f'Analyze these documents to answer: "{query_text}"\n\n'
                "Document Context:\n"
                f"{context_string}\n\n"
                "Instructions:\n"
                "1. Pay special attention to leadership sections and tables\n"
                "2. If mentioning people, include their titles and roles\n"
                "3. Reference specific pages/tables when possible\n"
                '4. If unsure, say "The documents state..." instead of assuming.'
            )

            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are a meticulous document analyst. Always: "
                    "- Stick strictly to provided content\n- Acknowledge uncertainty\n- Cite sources"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
                
        except Exception as e:
            print(f"Query Error: {str(e)}")
            return "Error processing request"