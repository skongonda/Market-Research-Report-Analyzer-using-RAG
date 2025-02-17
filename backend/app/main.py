from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from app.rag_system import RAGSystem
import os
import shutil
import uvicorn

# Initialize the FastAPI app
# Add custom middleware for large files
middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"]
    )
]

app = FastAPI(middleware=middleware)

# Initialize RAGSystem at the start
rag_system = RAGSystem()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local frontend (optional)
        "https://market-research-analyzer-rag.netlify.app",  # Netlify URL
        
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Ensure the upload directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "Hello World"}

# endpoint
@app.post("/analyze/")
async def analyze_files_and_query(
    files: list[UploadFile] = File(..., max_size=100_000_000),  # 100MB limit
    query: str = Form(None)
):
    try:
        file_paths = []

        # Handle uploaded files
        if files:
            for file in files:
                file_path = os.path.join(UPLOAD_DIR, file.filename)
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                file_paths.append(file_path)

        if not file_paths and not query:
            raise HTTPException(status_code=400, detail="No valid PDF files or query provided.")

        # Process the query if provided
        if query:
            if not file_paths:
                raise HTTPException(status_code=400, detail="No PDF files provided for query.")
            response = rag_system.query(query, file_paths)
            return {"response": response}

        return {"message": "Files uploaded successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Clean up uploaded files after processing
        for file_path in file_paths:
            if os.path.exists(file_path) and file_path.startswith(UPLOAD_DIR):
                os.remove(file_path)

if __name__ == "__main__":
    # Use the $PORT environment variable provided by Render, or default to 10000
    port = int(os.environ.get("PORT", 10000))
    
    # Start the app with Uvicorn and bind it to 0.0.0.0 and the selected port
    uvicorn.run(app, host="0.0.0.0", port=port)
