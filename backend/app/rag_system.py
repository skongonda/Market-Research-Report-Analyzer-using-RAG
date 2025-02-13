TABLE_SEPARATOR = "---TABLE_CONTENT---"

from openai import OpenAI
import numpy as np
from scipy.spatial.distance import cosine
from utils import load_environment, with_retry
import os
import pdfplumber
import re
from pdf2image import convert_from_path
import pytesseract
import pdfplumber
import logging

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class RAGSystem:
    def __init__(self):
        self.api_key = load_environment()
        self.client = OpenAI(api_key=self.api_key)  # Initialize OpenAI client
        self.table_separator = "=== TABLE ==="
        self.poppler_path = self._get_poppler_path()

    def _get_poppler_path(self):
        """Find Poppler path or return None"""
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

    def extract_text_from_pdf(self, file_path, max_pages=5):
        """
        Extract text from PDF with OCR fallback and detailed logging
        Returns: Extracted text or empty string
        """
        text = ""
        try:
            # First attempt: Standard text extraction
            with pdfplumber.open(file_path) as pdf:
                logging.info(f"Processing {file_path} with standard extraction")
                
                for i, page in enumerate(pdf.pages[:max_pages]):
                    page_text = page.extract_text() or ""
                    if page_text:
                        text += f"\nPAGE {i+1} TEXT:\n{page_text}"
                        logging.info(f"Extracted text from page {i+1}")
                        
                    # Table handling
                    tables = page.extract_tables()
                    if tables:
                        text += f"\nPAGE {i+1} TABLES: {len(tables)} table(s) found"
                        logging.info(f"Found {len(tables)} tables on page {i+1}")

            # If no text found, try OCR
            if not text.strip():
                logging.warning("No text found via standard extraction. Attempting OCR")
                try:
                    images = convert_from_path(
                        file_path,
                        first_page=1,
                        last_page=max_pages,
                        poppler_path=self.poppler_path
                    )
                    text = "\n".join([pytesseract.image_to_string(img) for img in images])
                    logging.info(f"OCR extracted {len(text.split())} words")
                except Exception as ocr_error:
                    logging.error(f"OCR failed: {str(ocr_error)}")
                    return ""

            # Final validation
            if not text.strip():
                logging.error("No content found in document")
                return ""
                
            return text

        except Exception as e:
            logging.error(f"Failed to process {file_path}: {str(e)}")
            return ""

    def get_embedding(self, text):
        """Generate embedding for text, ensuring valid input"""
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
        """Process user query and generate a response"""
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
            prompt = f"""Analyze these documents to answer: "{query_text}"
                        
            Document Context:
            {''.join([f'\n\n### Context {i+1}:\n{c}' for i, c in enumerate(context)])}

            Instructions:
            1. Pay special attention to leadership sections and tables
            2. If mentioning people, include their titles and roles
            3. Reference specific pages/tables when possible
            4. If unsure, say "The documents state..." instead of assuming"""

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
