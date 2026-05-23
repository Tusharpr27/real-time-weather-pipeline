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

export interface PressureChartProps {
  labels: string[];
  data: number[];
  loading?: boolean;
}

export const PressureChart: React.FC<PressureChartProps> = ({
  labels,
  data,
  loading = false,
}) => {
  const datasets = [
    {
      label: 'Atmospheric Pressure (hPa)',
      data,
      borderColor: 'rgb(99, 102, 241)',
      backgroundColor: 'rgba(99, 102, 241, 0.1)',
      fill: true,
      tension: 0.4,
      pointRadius: 4,
      pointBackgroundColor: 'rgb(99, 102, 241)',
      pointBorderColor: '#fff',
      pointBorderWidth: 2,
    },
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
            return `${context.dataset.label}: ${context.parsed.y.toFixed(1)} hPa`;
          },
        },
      },
    },
    scales: {
      y: {
        ticks: {
          callback: (value: any) => `${value}hPa`,
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
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Atmospheric Pressure</h3>
      <div className="h-80">
        <Line data={{ labels, datasets }} options={options} />
      </div>
    </Card>
  );
};

PressureChart.displayName = 'PressureChart';
