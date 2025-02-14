import API_BASE_URL from '../config';
import React, { useState } from 'react';
import axios from 'axios';
import { Button, Typography, Box, LinearProgress, Grid } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';

const FileUpload = ({ onUpload, onFilesChange }) => {
    const [files, setFiles] = useState([]);
    const [loading, setLoading] = useState(false);

    const handleFileChange = (e) => {
        const selectedFiles = [...e.target.files];
        // Validate file types
        const validFiles = selectedFiles.filter(file => 
            file.type === 'application/pdf'
        );
        if (validFiles.length !== selectedFiles.length) {
            alert("Only PDF files are allowed");
        }
        setFiles(validFiles);
        onFilesChange(validFiles);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (files.length < 1 || files.length > 3) {
            alert("Please upload 1 to 3 PDF files.");
            return;
        }
      
        setLoading(true);
      
        // Define formData here
        const formData = new FormData();
        files.forEach((file) => formData.append("files", file));
        formData.append("query", "Initial analysis");  // Default query
      
        try {
            const response = await axios.post(
                `${API_BASE_URL}/analyze/`,
                formData,
                {
                    headers: { 
                        "Content-Type": "multipart/form-data",
                        "X-Requested-With": "XMLHttpRequest"
                    },
                    timeout: 30000,  // 30 seconds timeout
                    withCredentials: true,
                }
            );
      
            if (response?.data?.response) {
                onUpload(response.data);
            } else {
                throw new Error(response?.data?.error || "Invalid server response");
            }
      
            setFiles([]);
        } catch (error) {
            console.error("Full error:", error);
            let errorMessage = "An error occurred";
            
            if (error.response) {
                // Backend returned error
                errorMessage = error.response.data?.detail || 
                             error.response.data?.error || 
                             `Server error: ${error.response.status}`;
            } else if (error.request) {
                // No response received
                errorMessage = "Server is not responding. Check:\n1. Backend status\n2. Network connection\n3. CORS configuration";
            } else {
                // Setup error
                errorMessage = error.message || "Request setup failed";
            }
            
            alert(`Error: ${errorMessage}`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="card">
            <div className="upload-section">
                <Typography variant="h5" gutterBottom style={{ color: '#2c3e50', marginBottom: '1.5rem' }}>
                    <CloudUploadIcon style={{ marginRight: '0.5rem', fontSize: '2rem' }} />
                    Upload Market Research Reports
                </Typography>
                
                <Grid container spacing={2} justifyContent="center" alignItems="center">
                    <Grid item>
                        <input
                            type="file"
                            multiple
                            onChange={handleFileChange}
                            accept="application/pdf"
                            style={{ display: 'none' }}
                            id="file-upload"
                        />
                        <label htmlFor="file-upload">
                            <Button
                                variant="contained"
                                component="span"
                                className="button-primary"
                                startIcon={<InsertDriveFileIcon />}
                            >
                                Select PDF Files
                            </Button>
                        </label>
                    </Grid>
                    <Grid item>
                        <Button
                            variant="contained"
                            className="button-primary"
                            onClick={handleSubmit}
                            disabled={loading}
                        >
                            {loading ? "Processing..." : "Analyze Files"}
                        </Button>
                    </Grid>
                </Grid>

                {files.length > 0 && (
                    <Box mt={3}>
                        <Typography variant="subtitle1" style={{ color: '#7f8c8d' }}>
                            Selected Files:
                        </Typography>
                        <ul className="file-list">
                            {files.map((file, index) => (
                                <li key={index}>
                                    <InsertDriveFileIcon style={{ color: '#3498db' }} />
                                    {file.name}
                                </li>
                            ))}
                        </ul>
                    </Box>
                )}

                {loading && <LinearProgress style={{ marginTop: '1rem', borderRadius: '8px' }} />}
            </div>
        </div>
    );
};

export default FileUpload;