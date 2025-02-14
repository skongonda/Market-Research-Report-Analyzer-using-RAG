TABLE_SEPARATOR = "---TABLE_CONTENT---"

from openai import OpenAI
import numpy as np
from scipy.spatial.distance import cosine
from .utils import load_environment, with_retry
import os
import pdfplumber
from pdf2image import convert_from_bytes
import pytesseract
import logging

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

        # Set paths for Poppler and Tesseract
        self.poppler_path = os.getenv('POPPLER_PATH', r'C:\Users\skong\AppData\Roaming\Release-24.08.0-0\poppler-24.08.0\Library\bin')
        self.tessdata_prefix = os.getenv('TESSDATA_PREFIX', r'C:\Program Files\Tesseract-OCR\tessdata')

        # Configure Tesseract
        self._configure_tesseract()

    def _configure_tesseract(self):
        """Configure Tesseract based on the environment."""
        try:
            if os.name == 'nt':  # Windows
                # Set Tesseract path for Windows
                pytesseract.pytesseract.tesseract_cmd = os.path.join(
                    os.path.dirname(self.tessdata_prefix), 
                    'tesseract.exe'
                )
            else:  # Linux (Render)
                # Set Tesseract path for Linux
                pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
                os.environ['TESSDATA_PREFIX'] = '/usr/share/tesseract-ocr/4.00/tessdata'

            # Verify Tesseract installation
            if not os.path.exists(pytesseract.pytesseract.tesseract_cmd):
                raise RuntimeError(f"Tesseract not found at {pytesseract.pytesseract.tesseract_cmd}")
            
            logging.info(f"Tesseract configured successfully at {pytesseract.pytesseract.tesseract_cmd}")
        except Exception as e:
            logging.error(f"Tesseract configuration failed: {str(e)}")
            raise RuntimeError("Tesseract OCR not properly installed") from e

    def extract_text_from_pdf(self, file_path, max_pages=5):
        """
        Extract text from PDF with OCR fallback.
        """
        text = ""
        try:
            # First attempt: Extract text using pdfplumber
            with pdfplumber.open(file_path) as pdf:
                logging.info(f"Processing {file_path} with standard extraction")
                
                for i, page in enumerate(pdf.pages[:max_pages]):
                    page_text = page.extract_text() or ""
                    if page_text:
                        text += f"\nPAGE {i+1} TEXT:\n{page_text}"
                        logging.info(f"Extracted text from page {i+1}")
                    
                    # Extract tables
                    tables = page.extract_tables()
                    if tables:
                        text += f"\nPAGE {i+1} TABLES: {len(tables)} table(s) found"
                        logging.info(f"Found {len(tables)} tables on page {i+1}")

            # Fallback to OCR if no text is found
            if not text.strip():
                logging.warning("No text found via standard extraction. Attempting OCR")
                try:
                    with open(file_path, "rb") as f:
                        images = convert_from_bytes(
                            f.read(),
                            first_page=1,
                            last_page=max_pages,
                            poppler_path=self.poppler_path
                        )
                        text = "\n".join([
                            pytesseract.image_to_string(
                                img, 
                                config='--psm 3 --oem 3'  # Improved OCR settings
                            ) for img in images
                        ])
                        logging.info(f"OCR extracted {len(text.split())} words")
                except Exception as ocr_error:
                    logging.error(f"OCR failed: {str(ocr_error)}")
                    return ""

            # Validate content
            if not self._validate_content(text):
                logging.error("No valid content found in document")
                return ""
                
            return text

        except Exception as e:
            logging.error(f"Failed to process {file_path}: {str(e)}")
            return ""

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
            all_chunks = []
            for file_path in file_paths:
                text = self.extract_text_from_pdf(file_path)
                if not text:
                    continue
                chunks = self.chunk_text(text)
                for chunk in chunks:
                    embedding = self.get_embedding(chunk)
                    all_chunks.append((chunk, embedding, file_path))

            if not all_chunks:
                return "Error: No valid content found in documents"

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