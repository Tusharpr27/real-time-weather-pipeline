import React, { useState } from 'react';
import { useChartData, TIME_RANGES } from '@/hooks/useChartData';
import { PageContainer, Divider } from '@/components/common';
import { Button, Tabs } from '@/components/ui';
import {
  TemperatureTrendChart,
  HumidityChart,
  PressureChart,
  WindSpeedChart,
  PrecipitationChart,
  ComparisonChart,
  GaugeChart,
} from '@/components/charts';
import { Calendar } from 'lucide-react';

const History: React.FC = () => {
  const [selectedTimeRange, setSelectedTimeRange] = useState<keyof typeof TIME_RANGES>('24h');
  const {
    temperatureData,
    humidityData,
    pressureData,
    windData,
    precipitationData,
    loading,
    selectedLocation,
  } = useChartData(selectedTimeRange);

  // Calculate current averages for gauge display
  const avgTemperature =
    temperatureData.current.reduce((a, b) => a + b, 0) / temperatureData.current.length;
  const avgHumidity =
    humidityData.current.reduce((a, b) => a + b, 0) / humidityData.current.length;

  // Prepare comparison chart data
  const comparisonDatasets = [
    {
      label: 'Temperature (°C)',
      data: temperatureData.current,
      borderColor: 'rgb(239, 68, 68)',
      backgroundColor: 'rgba(239, 68, 68, 0.1)',
    },
    {
      label: 'Humidity (÷5 for scale)',
      data: humidityData.current.map((h) => h / 5),
      borderColor: 'rgb(34, 197, 94)',
      backgroundColor: 'rgba(34, 197, 94, 0.1)',
    },
  ];

  const tabOptions = [
    { id: '24h', label: 'Last 24 Hours' },
    { id: '7d', label: 'Last 7 Days' },
    { id: '30d', label: 'Last 30 Days' },
    { id: '90d', label: 'Last 90 Days' },
    { id: '1y', label: 'Last Year' },
  ];

  return (
    <div className="flex-1 bg-gray-50">
      <PageContainer maxWidth="6xl" padding="lg">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900">Weather Analytics</h1>
          <p className="text-gray-600 mt-2">
            Historical weather data and trends for {selectedLocation || 'your location'}
          </p>
        </div>

        <Divider spacing="lg" />

        {/* Time Range Selector */}
        <div className="mb-8 bg-white rounded-lg shadow-sm p-4 border border-gray-200">
          <div className="flex items-center gap-2 mb-4">
            <Calendar className="w-5 h-5 text-gray-600" />
            <h3 className="text-sm font-semibold text-gray-700">Select Time Range</h3>
          </div>
          <Tabs
            tabs={tabOptions}
            defaultValue="24h"
            onChange={(value) => setSelectedTimeRange(value as keyof typeof TIME_RANGES)}
            className="flex flex-wrap gap-2"
          />
        </div>

        <Divider spacing="lg" />

        {/* Quick Stats Row */}
        <div className="mb-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          <GaugeChart
            value={avgTemperature}
            maxValue={50}
            unit="°C"
            label="Avg Temperature"
            color="rgb(239, 68, 68)"
            loading={loading}
          />
          <GaugeChart
            value={avgHumidity}
            maxValue={100}
            unit="%"
            label="Avg Humidity"
            color="rgb(34, 197, 94)"
            loading={loading}
          />
        </div>

        <Divider spacing="lg" />

        {/* Temperature Chart */}
        <div className="mb-8">
          <TemperatureTrendChart
            labels={temperatureData.labels}
            data={temperatureData.current}
            minTemp={temperatureData.min}
            maxTemp={temperatureData.max}
            loading={loading}
          />
        </div>

        <Divider spacing="lg" />

        {/* Two Column Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Humidity Chart */}
          <HumidityChart
            labels={humidityData.labels}
            data={humidityData.current}
            avgData={humidityData.avg}
            loading={loading}
          />

          {/* Pressure Chart */}
          <PressureChart
            labels={pressureData.labels}
            data={pressureData.data}
            loading={loading}
          />
        </div>

        <Divider spacing="lg" />

        {/* Wind and Precipitation Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Wind Speed Chart */}
          <WindSpeedChart
            labels={windData.labels}
            data={windData.speed}
            gustData={windData.gust}
            loading={loading}
          />

          {/* Precipitation Chart */}
          <PrecipitationChart
            labels={precipitationData.labels}
            data={precipitationData.data}
            probability={precipitationData.probability}
            loading={loading}
          />
        </div>

        <Divider spacing="lg" />

        {/* Comparison Chart - Full Width */}
        <div className="mb-8">
          <ComparisonChart
            labels={temperatureData.labels}
            datasets={comparisonDatasets}
            title="Temperature vs Humidity Comparison"
            loading={loading}
            yAxisLabel="Value"
          />
        </div>

        <Divider spacing="lg" />

        {/* Data Export Section */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Export Data</h3>
          <p className="text-gray-600 mb-4">
            Download historical weather data for analysis and reporting
          </p>
          <div className="flex flex-wrap gap-3">
            <Button
              variant="primary"
              onClick={() => {
                console.log('Export JSON');
              }}
            >
              Export as JSON
            </Button>
            <Button
              variant="secondary"
              onClick={() => {
                console.log('Export CSV');
              }}
            >
              Export as CSV
            </Button>
            <Button
              variant="secondary"
              onClick={() => {
                console.log('Export PDF');
              }}
            >
              Export as PDF
            </Button>
          </div>
        </div>
      </PageContainer>
    </div>
  );
};

export default History;
