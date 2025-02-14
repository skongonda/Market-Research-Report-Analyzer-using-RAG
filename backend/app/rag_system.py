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
import subprocess

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
        self.poppler_path = os.getenv('POPPLER_PATH', r'C:\Users\skong\AppData\Roaming\Release-24.08.0-0\poppler-24.08.0\Library\bin')  # Fallback for local dev
        self.tessdata_prefix = os.getenv('TESSDATA_PREFIX', r'C:\Program Files\Tesseract-OCR\tessdata')

        # Configure Tesseract
        self._configure_tesseract()

        # Validate OCR setup during initialization
        self._verify_ocr_setup()

    def _configure_tesseract(self):
        """Configure Tesseract based on the environment."""
        try:
            if os.name == 'nt':  # Windows
                pytesseract.pytesseract.tesseract_cmd = os.path.join(
                    os.path.dirname(self.tessdata_prefix), 
                    'tesseract.exe'
                )
            else:  # Linux (Render)
                pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
                os.environ['TESSDATA_PREFIX'] = '/usr/share/tesseract-ocr/4.00/tessdata'

            # Verify Tesseract installation
            subprocess.run([pytesseract.pytesseract.tesseract_cmd, '--version'], 
                          check=True, capture_output=True)
        except Exception as e:
            logging.error(f"Tesseract verification failed: {str(e)}")
            raise RuntimeError("Tesseract OCR not properly installed") from e

    def _verify_ocr_setup(self):
        """Validate OCR dependencies are properly installed."""
        try:
            # Test OCR with a simple image
            test_image = pytesseract.image_to_string('test.png')
            if not test_image:
                raise RuntimeError("OCR returned empty text")
        except Exception as e:
            logging.error(f"OCR setup validation failed: {str(e)}")
            raise

    def _get_poppler_path(self):
        """Find Poppler path or return None."""
        if os.name == 'nt':  # Windows
            paths = [
                r"C:\poppler\bin",
                r"C:\Program Files\poppler\bin",
                r"C:\Program Files (x86)\poppler\bin"
            ]
            for path in paths:
                if os.path.exists(path):
                    return path
        return None

    def summarize_text(self, text, max_tokens=200):
        """Summarize a given text using OpenAI API."""
        response = self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "system", "content": "Summarize this text:"},
                      {"role": "user", "content": text}],
            max_tokens=max_tokens
        )
        summary = response.choices[0].message.content if response.choices else "No summary available."
        return summary.strip()
    
    def chunk_text(self, text, max_tokens=1000):
        """Split text into chunks of max_tokens."""
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

    def extract_text_from_pdf(self, file_path, max_pages=5):
        """
        Enhanced PDF text extraction with better OCR handling.
        """
        text = ""
        try:
            # First attempt: Improved text extraction with layout preservation
            with pdfplumber.open(file_path) as pdf:
                logging.info(f"Processing {file_path} with enhanced extraction")
                
                for i, page in enumerate(pdf.pages[:max_pages]):
                    # Extract text with layout awareness
                    page_text = page.extract_text(
                        x_tolerance=1, 
                        y_tolerance=3,
                        keep_blank_chars=True,
                        use_text_flow=True
                    ) or ""
                    
                    # Extract tables with improved detection
                    tables = page.find_tables()
                    if tables:
                        page_text += f"\n{self.table_separator}\n"
                        page_text += "\n\n".join(
                            [str(table.extract()) for table in tables]
                        )
                    
                    text += f"\nPAGE {i+1}:\n{page_text}"

            # Fallback to OCR only if no text detected
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

            # Content validation with improved checks
            if not self._validate_content(text):
                logging.error("No valid content found in document")
                return ""
                
            return text

        except Exception as e:
            logging.error(f"Failed to process {file_path}: {str(e)}")
            return ""
        
    def _validate_content(self, text):
        """Enhanced content validation."""
        # Check for minimum meaningful content
        words = [w for w in text.split() if len(w) > 3]
        return len(words) > 50  # Require at least 50 meaningful words

    def get_embedding(self, text):
        """Generate embedding for text, ensuring valid input."""
        try:
            # Clean and truncate text to fit OpenAI's input limits
            clean_text = text.replace("\n", " ").replace("  ", " ").strip()
            if len(clean_text) > 8000:  # OpenAI's max input size
                clean_text = clean_text[:8000]
            
            # Ensure the input is a non-empty string
            if not clean_text:
                return np.zeros(1536)  # Return a zero vector if no text
            
            # Generate embedding
            response = with_retry(lambda: self.client.embeddings.create(
                input=[clean_text],  # Must be a list of strings
                model="text-embedding-3-small"
            ))
            return np.array(response.data[0].embedding)
        except Exception as e:
            print(f"Embedding Error: {str(e)}")
            return np.zeros(1536)  # Fallback to zero vector

    def query(self, query_text, file_paths):
        """Process user query and generate a response."""
        try:
            # 1. Process all documents
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

            # 2. Semantic search
            query_embedding = self.get_embedding(query_text)
            results = []
            for chunk, emb, path in all_chunks:
                similarity = 1 - cosine(query_embedding, emb)
                results.append((similarity, chunk, path))

            # 3. Get top 5 relevant chunks
            results.sort(reverse=True, key=lambda x: x[0])
            top_chunks = results[:5]

            # 4. Build context
            context = []
            for score, chunk, path in top_chunks:
                source = f"From {path.split('/')[-1]}"
                if self.table_separator in chunk:
                    context.append(f"TABLE DATA ({source}):\n{chunk.split(self.table_separator)[-1]}")
                else:
                    context.append(f"TEXT CONTENT ({source}):\n{chunk}")

            # 5. Generate prompt
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

            # 6. Get LLM response
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