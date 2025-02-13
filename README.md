# Market Research Report Analyzer

### Project Overview

This project is a web application that implements a Retrieval-Augmented Generation (RAG) backend system to analyze and compare market research reports. The application allows users to upload two market research reports, ask questions in natural language, and receive AI-powered insights and comparisons. The backend is built using Python and FastAPI, while the frontend is developed using React and Material-UI.

#### Key Features:

AI-Powered Insights: Users can ask questions about the uploaded reports, and the system will generate insights using a RAG pipeline.

Source Data: All results are backed by source data, which can be double-clicked to view the original content.

User-Friendly Interface: The frontend provides an intuitive interface for uploading files, asking questions, and viewing results.

Error Handling: The system includes robust error handling and loading state management.

## Step-by-Step Process:

1. Backend Development

1.1. FastAPI Server
The backend is built using FastAPI, a modern Python web framework for building APIs.

The server acts as an intermediary between the frontend and the RAG system.

It handles file uploads, processes user queries, and interacts with the RAG system to generate insights.

1.2. RAG System
The Retrieval-Augmented Generation (RAG) system is the core of the backend.

It processes the uploaded PDF reports, extracts text, and generates embeddings using OpenAI's text-embedding-3-small model.

The system uses semantic search to retrieve relevant information from the reports based on user queries.

The retrieved information is then passed to OpenAI's GPT-4 Turbo model to generate insightful responses.

1.3. PDF Processing
The backend uses pdfplumber and pytesseract to extract text from PDF files.

If the text extraction fails, the system falls back to OCR (Optical Character Recognition) using Tesseract.

The extracted text is chunked into smaller pieces for efficient processing and embedding generation.

1.4. Embeddings and Semantic Search
The system generates vector embeddings for each text chunk using OpenAI's embedding model.

When a user query is received, the system computes the similarity between the query embedding and the document embeddings using cosine similarity.

The top 5 most relevant chunks are selected and passed to the GPT-4 Turbo model for generating the final response.

1.5. Error Handling and Retry Logic
The backend includes robust error handling and retry logic to handle API rate limits and other potential errors.

The with_retry function ensures that the system retries failed requests with exponential backoff.

2. Frontend Development

2.1. React Framework
The frontend is built using React, a popular JavaScript library for building user interfaces.

The application uses React Router for navigation between different pages (e.g., Home and Insights).

2.2. Material-UI Components
The frontend uses Material-UI components for a clean and responsive user interface.

Components like Button, TextField, Typography, and LinearProgress are used to create a consistent and user-friendly design.

2.3. File Upload Component
The FileUpload component allows users to upload 1 to 3 PDF files.

The component handles file selection, validation, and upload to the backend.

It also displays the selected files and shows a loading state during file processing.

2.4. Query Input Component
The QueryInput component allows users to enter natural language queries about the uploaded reports.

The component sends the query and uploaded files to the backend for processing and displays the generated insights.

2.5. Response Display
The backend's response is displayed in the Home component.

The response includes AI-generated insights, and users can double-click to view the source data.

2.6. Insights Page
The Insights page is a placeholder for future features, such as visualizing insights using charts or graphs.

3. Deployment
   The application can be deployed using platforms like Vercel, Render, or Heroku.

The backend can be deployed as a standalone FastAPI server, while the frontend can be deployed as a static React application.

---

# Technologies Used

Backend:

Python: The primary programming language for the backend.

FastAPI: A modern, fast (high-performance) web framework for building APIs with Python.

OpenAI GPT-4 Turbo: A state-of-the-art language model used for generating insights.

OpenAI Embeddings: Used for generating vector embeddings of text chunks.

pdfplumber: A library for extracting text and tables from PDF files.

pytesseract: A Python wrapper for Tesseract OCR, used for text extraction from scanned PDFs.

Flask-CORS: Middleware for handling Cross-Origin Resource Sharing (CORS) in the backend.

Frontend:

React: A JavaScript library for building user interfaces.

Material-UI: A popular React UI framework for building responsive and visually appealing components.

React Router: A library for handling navigation between different pages in a React application.

Axios: A promise-based HTTP client for making API requests to the backend.

# How to Run the Project

#### Backend:

Install the required Python packages: pip install fastapi uvicorn openai pdfplumber pytesseract python-dotenv

Set up your OpenAI API key in a .env file: OPENAI_API_KEY=your_openai_api_key

Run the FastAPI server: uvicorn app.main:app --reload

#### Frontend:

Install the required Node.js packages: npm install

Start the React development server: npm start

# Conclusion

This project demonstrates the power of combining Retrieval-Augmented Generation (RAG) with modern web development tools to create a user-friendly application for analyzing and comparing market research reports. The system leverages state-of-the-art AI models to provide insightful and accurate responses, backed by source data from the uploaded reports.
