import React, { useState } from 'react';
import FileUpload from '../components/FileUpload';
import QueryInput from '../components/QueryInput';
import { Container, Typography } from '@mui/material';

const Home = () => {
    const [response, setResponse] = useState(null);
    const [files, setFiles] = useState([]);

    const handleUpload = (uploadData) => {
        setResponse(uploadData.message);
    };

    const handleQuery = (queryData) => {
        setResponse(queryData.response);
    };

    return (
        <div className="container">
            <nav>
                <h1>Market Research Analyzer</h1>
            </nav>

            <Container maxWidth="md">
                <FileUpload 
                    onUpload={handleUpload} 
                    onFilesChange={(selectedFiles) => setFiles(selectedFiles)}
                />
                
                <QueryInput onQuery={handleQuery} files={files} />

                {response && (
                    <div className="response-section">
                        <Typography variant="h6" gutterBottom style={{ color: '#2c3e50' }}>
                            📊 Analysis Results
                        </Typography>
                        <Typography variant="body1" className="response-text">
                            {response}
                        </Typography>
                    </div>
                )}
            </Container>
        </div>
    );
};

export default Home;