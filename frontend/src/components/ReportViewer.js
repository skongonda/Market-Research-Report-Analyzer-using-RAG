import React from 'react';
import { Paper, Typography, Box } from '@mui/material';

const ReportViewer = ({ tables = [], charts = [] }) => {
    return (
        <Paper elevation={3} style={{ padding: '20px', marginBottom: '20px' }}>
            <Typography variant="h5" gutterBottom>
                Extracted Tables
            </Typography>
            {tables.length > 0 ? (
                tables.map((table, index) => (
                    <Box key={index} style={{ marginBottom: '20px' }}>
                        <pre>{JSON.stringify(table, null, 2)}</pre>
                    </Box>
                ))
            ) : (
                <Typography variant="body1" color="textSecondary">
                    No tables found.
                </Typography>
            )}
            <Typography variant="h5" gutterBottom>
                Extracted Charts
            </Typography>
            {charts.length > 0 ? (
                charts.map((chart, index) => (
                    <Box key={index} style={{ marginBottom: '20px' }}>
                        <pre>{JSON.stringify(chart, null, 2)}</pre>
                    </Box>
                ))
            ) : (
                <Typography variant="body1" color="textSecondary">
                    No charts found.
                </Typography>
            )}
        </Paper>
    );
};

export default ReportViewer;