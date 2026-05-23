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

export interface ComparisonDataset {
  label: string;
  data: number[];
  borderColor: string;
  backgroundColor: string;
}

export interface ComparisonChartProps {
  labels: string[];
  datasets: ComparisonDataset[];
  title?: string;
  loading?: boolean;
  yAxisLabel?: string;
}

export const ComparisonChart: React.FC<ComparisonChartProps> = ({
  labels,
  datasets,
  title = 'Weather Comparison',
  loading = false,
  yAxisLabel = 'Value',
}) => {
  const chartDatasets = datasets.map((ds) => ({
    label: ds.label,
    data: ds.data,
    borderColor: ds.borderColor,
    backgroundColor: ds.backgroundColor,
    fill: false,
    tension: 0.4,
    pointRadius: 3,
    pointBackgroundColor: ds.borderColor,
    pointBorderColor: '#fff',
    pointBorderWidth: 1,
  }));

  const options = {
    responsive: true,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
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
      },
    },
    scales: {
      y: {
        ticks: {
          font: { size: 11 },
        },
        grid: { color: 'rgba(0, 0, 0, 0.05)' },
        title: {
          display: true,
          text: yAxisLabel,
          font: { size: 12, weight: 600 },
        },
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
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      <div className="h-80">
        <Line data={{ labels, datasets: chartDatasets }} options={options} />
      </div>
    </Card>
  );
};

ComparisonChart.displayName = 'ComparisonChart';
