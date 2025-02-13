import React, { useState } from 'react';
import axios from 'axios';
import { Button, TextField, Typography, Grid } from '@mui/material';
import QuestionAnswerIcon from '@mui/icons-material/QuestionAnswer';

const QueryInput = ({ onQuery, files }) => {
    const [query, setQuery] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!query) {
            alert("Please enter a query.");
            return;
        }

        if (!files || files.length === 0) {
            alert("Please upload files before asking a question.");
            return;
        }

        const formData = new FormData();
        files.forEach((file) => formData.append('files', file));
        formData.append('query', query);

        try {
            const response = await axios.post('http://localhost:8000/analyze/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            onQuery(response.data);
        } catch (error) {
            console.error('Error querying:', error);
            alert(error.response?.data?.detail || "Failed to process query.");
        }
    };

    return (
        <div className="card">
            <Typography variant="h5" gutterBottom style={{ color: '#2c3e50', marginBottom: '1.5rem' }}>
                <QuestionAnswerIcon style={{ marginRight: '0.5rem', color: '#3498db' }} />
                Ask Your Question
            </Typography>
            
            <Grid container spacing={2} alignItems="center">
                <Grid item xs={12} md={9}>
                    <TextField
                        fullWidth
                        variant="outlined"
                        placeholder="Example: Compare the financial performance between Q3 and Q4..."
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        InputProps={{
                            style: {
                                borderRadius: '8px',
                                fontSize: '1.1rem',
                                padding: '12px 16px'
                            }
                        }}
                    />
                </Grid>
                <Grid item xs={12} md={3}>
                    <Button
                        fullWidth
                        variant="contained"
                        className="button-primary"
                        onClick={handleSubmit}
                        style={{ height: '56px' }}
                    >
                        Get Insights
                    </Button>
                </Grid>
            </Grid>
        </div>
    );
};

export default QueryInput;