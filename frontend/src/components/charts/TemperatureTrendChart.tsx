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
  Filler,
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
  Legend,
  Filler
);

export interface TemperatureTrendChartProps {
  labels: string[];
  data: number[];
  minTemp?: number[];
  maxTemp?: number[];
  loading?: boolean;
}

export const TemperatureTrendChart: React.FC<TemperatureTrendChartProps> = ({
  labels,
  data,
  minTemp,
  maxTemp,
  loading = false,
}) => {
  const datasets = [
    {
      label: 'Current Temperature (°C)',
      data,
      borderColor: 'rgb(239, 68, 68)',
      backgroundColor: 'rgba(239, 68, 68, 0.1)',
      fill: true,
      tension: 0.4,
      pointRadius: 4,
      pointBackgroundColor: 'rgb(239, 68, 68)',
      pointBorderColor: '#fff',
      pointBorderWidth: 2,
    },
    ...(maxTemp
      ? [
          {
            label: 'Max Temperature (°C)',
            data: maxTemp,
            borderColor: 'rgb(251, 146, 60)',
            backgroundColor: 'transparent',
            fill: false,
            tension: 0.4,
            borderDash: [5, 5],
            pointRadius: 3,
            pointBackgroundColor: 'rgb(251, 146, 60)',
          },
        ]
      : []),
    ...(minTemp
      ? [
          {
            label: 'Min Temperature (°C)',
            data: minTemp,
            borderColor: 'rgb(59, 130, 246)',
            backgroundColor: 'transparent',
            fill: false,
            tension: 0.4,
            borderDash: [5, 5],
            pointRadius: 3,
            pointBackgroundColor: 'rgb(59, 130, 246)',
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
            return `${context.dataset.label}: ${context.parsed.y}°C`;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: false,
        ticks: {
          callback: (value: any) => `${value}°C`,
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
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Temperature Trend</h3>
      <div className="h-80">
        <Line data={{ labels, datasets }} options={options} />
      </div>
    </Card>
  );
};

TemperatureTrendChart.displayName = 'TemperatureTrendChart';
