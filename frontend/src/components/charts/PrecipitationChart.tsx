import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import { Card } from '@/components/ui';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

export interface PrecipitationChartProps {
  labels: string[];
  data: number[];
  probability?: number[];
  loading?: boolean;
}

export const PrecipitationChart: React.FC<PrecipitationChartProps> = ({
  labels,
  data,
  probability,
  loading = false,
}) => {
  const datasets = [
    {
      label: 'Precipitation (mm)',
      data,
      backgroundColor: 'rgba(59, 130, 246, 0.7)',
      borderColor: 'rgb(59, 130, 246)',
      borderWidth: 1,
      borderRadius: 6,
    },
    ...(probability
      ? [
          {
            label: 'Probability (%)',
            data: probability.map((p) => (p / 100) * Math.max(...data)),
            backgroundColor: 'rgba(168, 85, 247, 0.5)',
            borderColor: 'rgb(168, 85, 247)',
            borderWidth: 1,
            borderRadius: 6,
          },
        ]
      : []),
  ];

  const options = {
    indexAxis: 'x' as const,
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
            if (context.datasetIndex === 0) {
              return `${context.dataset.label}: ${context.parsed.y.toFixed(1)} mm`;
            } else {
              const origProbability = probability?.[context.dataIndex] || 0;
              return `${context.dataset.label}: ${origProbability}%`;
            }
          },
        },
      },
    },
    scales: {
      y: {
        ticks: {
          callback: (value: any) => `${value.toFixed(1)} mm`,
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
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Precipitation</h3>
      <div className="h-80">
        <Bar data={{ labels, datasets }} options={options} />
      </div>
    </Card>
  );
};

PrecipitationChart.displayName = 'PrecipitationChart';
