import React from 'react';
import Chart from '../components/Chart'; // Correct path

const Insights = ({ data }) => {
    return (
        <div className="insights-container">
            <h2>Insights</h2>
            {data && <Chart data={data} />}
        </div>
    );
};

export default Insights;