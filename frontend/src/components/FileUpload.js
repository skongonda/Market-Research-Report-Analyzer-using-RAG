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
        setFiles(selectedFiles);
        onFilesChange(selectedFiles);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (files.length < 1 || files.length > 3) {
            alert("Please upload 1 to 3 PDF files.");
            return;
        }
    
        setLoading(true);
        const formData = new FormData();
        files.forEach((file) => formData.append('files', file));
    
        try {
            const response = await axios.post(`${API_BASE_URL}/analyze/`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
                withCredentials: true,
            });
    
            if (response && response.data) {
                onUpload(response.data);
            } else {
                throw new Error("Invalid response from the server.");
            }
            setFiles([]);
        } catch (error) {
            console.error('Error uploading files:', error);
            if (error.response) {
                alert(error.response.data?.detail || "Failed to process files.");
            } else if (error.request) {
                alert("No response received from the server. Please check your network connection.");
            } else {
                alert("An error occurred while setting up the request.");
            }
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