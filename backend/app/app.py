from flask import Flask, request, jsonify
import os
from backend.app.rag_system import RAGSystem  # Import your RAG system
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["https://market-research-analyzer-rag.netlify.app"])

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload_files():
    uploaded_files = []
    if "files" not in request.files:
        return jsonify({"error": "No file part"}), 400

    files = request.files.getlist("files")
    for file in files:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        uploaded_files.append(file_path)

    return jsonify({"uploaded_files": uploaded_files})

@app.route("/query", methods=["POST"])
def query():
    data = request.json
    query_text = data.get("query", "")
    uploaded_files = data.get("uploaded_files", [])

    if not uploaded_files:
        return jsonify({"error": "No uploaded files provided"}), 400

    rag = RAGSystem(uploaded_files)  # Pass uploaded file paths
    response = rag.query(query_text, uploaded_files)

    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)
