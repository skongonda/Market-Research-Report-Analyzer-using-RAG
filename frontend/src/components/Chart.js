import React from 'react';
import { Bar } from 'react-chartjs-2';

const Chart = ({ data }) => {
    const chartData = {
        labels: data.labels,
        datasets: [
            {
                label: 'Chart Data',
                data: data.values,
                backgroundColor: 'rgba(75,192,192,0.4)',
                borderColor: 'rgba(75,192,192,1)',
                borderWidth: 1,
            },
        ],
    };

    return (
        <div className="chart-container">
            <Bar data={chartData} />
        </div>
    );
};

export default Chart;