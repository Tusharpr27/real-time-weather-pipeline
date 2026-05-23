import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { Card } from '@/components/ui';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

export interface WindSpeedChartProps {
  labels: string[];
  data: number[];
  gustData?: number[];
  loading?: boolean;
}

export const WindSpeedChart: React.FC<WindSpeedChartProps> = ({
  labels,
  data,
  gustData,
  loading = false,
}) => {
  const datasets = [
    {
      label: 'Wind Speed (m/s)',
      data,
      borderColor: 'rgb(14, 165, 233)',
      backgroundColor: 'rgba(14, 165, 233, 0.1)',
      fill: true,
      tension: 0.4,
      pointRadius: 4,
      pointBackgroundColor: 'rgb(14, 165, 233)',
      pointBorderColor: '#fff',
      pointBorderWidth: 2,
    },
    ...(gustData
      ? [
          {
            label: 'Wind Gust (m/s)',
            data: gustData,
            borderColor: 'rgb(236, 72, 153)',
            backgroundColor: 'transparent',
            fill: false,
            tension: 0.4,
            borderDash: [5, 5],
            pointRadius: 3,
            pointBackgroundColor: 'rgb(236, 72, 153)',
          },
        ]
      : []),
  ];

  const options = {
    responsive: true,
    plugins: {
      legend: {
        display: true,
        position: 'top' as const,
        labels: {
          usePointStyle: true,
          padding: 15,
          font: { size: 12, weight: 600 },
        },
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        padding: 12,
        titleFont: { size: 14, weight: 600 },
        bodyFont: { size: 12 },
        cornerRadius: 8,
        callbacks: {
          label: (context: any) => {
            return `${context.dataset.label}: ${context.parsed.y.toFixed(1)} m/s`;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: (value: any) => `${value} m/s`,
          font: { size: 11 },
        },
        grid: { color: 'rgba(0, 0, 0, 0.05)' },
      },
      x: {
        ticks: { font: { size: 11 } },
        grid: { display: false },
      },
    },
  };

  if (loading) {
    return (
      <Card className="p-6">
        <div className="h-80 bg-gray-100 rounded-lg animate-pulse" />
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Wind Speed</h3>
      <div className="h-80">
        <Line data={{ labels, datasets }} options={options} />
      </div>
    </Card>
  );
};

WindSpeedChart.displayName = 'WindSpeedChart';
