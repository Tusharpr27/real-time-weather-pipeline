import React from 'react';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js';
import { Doughnut } from 'react-chartjs-2';
import { Card } from '@/components/ui';

ChartJS.register(ArcElement, Tooltip, Legend);

export interface GaugeChartProps {
  value: number;
  maxValue?: number;
  unit?: string;
  label?: string;
  color?: string;
  loading?: boolean;
}

export const GaugeChart: React.FC<GaugeChartProps> = ({
  value,
  maxValue = 100,
  unit = '%',
  label = 'Gauge',
  color = 'rgb(59, 130, 246)',
  loading = false,
}) => {
  const percentage = (value / maxValue) * 100;
  const remaining = maxValue - value;

  const data = {
    labels: [label, 'Remaining'],
    datasets: [
      {
        data: [value, remaining],
        backgroundColor: [color, 'rgba(229, 231, 235, 0.5)'],
        borderColor: [color, 'rgba(229, 231, 235, 0.5)'],
        borderWidth: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        padding: 12,
        titleFont: { size: 14, weight: 600 },
        bodyFont: { size: 12 },
        cornerRadius: 8,
        callbacks: {
          label: (context: any) => {
            if (context.label === label) {
              return `${label}: ${context.parsed} ${unit}`;
            }
            return `Remaining: ${context.parsed} ${unit}`;
          },
        },
      },
    },
  };

  if (loading) {
    return (
      <Card className="p-6">
        <div className="h-48 bg-gray-100 rounded-lg animate-pulse" />
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <div className="text-center">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{label}</h3>
        <div className="flex justify-center mb-4">
          <div className="w-40 h-40">
            <Doughnut data={data} options={options} />
          </div>
        </div>
        <div className="text-3xl font-bold text-gray-900">
          {value.toFixed(1)}{unit}
        </div>
        <p className="text-sm text-gray-600 mt-2">
          {percentage.toFixed(0)}% of {maxValue}{unit}
        </p>
      </div>
    </Card>
  );
};

GaugeChart.displayName = 'GaugeChart';
