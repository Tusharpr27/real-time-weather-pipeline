import React from 'react';
import { WeatherCard } from '@/components/common';
import { WeatherData } from '@/types';
import { Skeleton } from '@/components/feedback';
import { EmptyState } from '@/components/data-display';
import { Grid } from '@/components/common';
import { Cloud } from 'lucide-react';

export interface WeatherGridProps {
  data: WeatherData[];
  loading?: boolean;
  gridCols?: 1 | 2 | 3 | 4;
  onCardClick?: (locationId: string) => void;
}

export const WeatherGrid: React.FC<WeatherGridProps> = ({
  data,
  loading = false,
  gridCols = 3,
  onCardClick,
}) => {
  if (loading) {
    return (
      <Grid cols={gridCols} gap="md">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="space-y-4">
            <Skeleton count={1} height="lg" variant="rect" />
            <Skeleton count={2} height="md" variant="text" />
            <Skeleton count={1} height="sm" variant="text" />
          </div>
        ))}
      </Grid>
    );
  }

  if (data.length === 0) {
    return (
      <EmptyState
        icon={<Cloud size={48} />}
        title="No Weather Data Available"
        description="No weather data found for selected locations. Try adding a new location or refresh the data."
      />
    );
  }

  return (
    <Grid cols={gridCols} gap="md">
      {data.map((weather) => (
        <WeatherCard
          key={weather.id}
          data={weather}
          onClick={() => onCardClick?.(weather.location?.id || '')}
        />
      ))}
    </Grid>
  );
};

WeatherGrid.displayName = 'WeatherGrid';
