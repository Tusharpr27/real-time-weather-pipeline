import { useCallback } from 'react';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import {
  fetchCurrentWeather,
  fetchWeatherForecast,
  setSelectedLocation,
} from '@/store/slices/weatherSlice';

export const useWeather = () => {
  const dispatch = useAppDispatch();
  const weather = useAppSelector((state) => state.weather);

  const getCurrentWeather = useCallback(
    (locationId: string) => {
      dispatch(fetchCurrentWeather(locationId));
    },
    [dispatch]
  );

  const getForecast = useCallback(
    (locationId: string) => {
      dispatch(fetchWeatherForecast(locationId));
    },
    [dispatch]
  );

  const selectLocation = useCallback(
    (locationId: string) => {
      dispatch(setSelectedLocation(locationId));
    },
    [dispatch]
  );

  return {
    ...weather,
    getCurrentWeather,
    getForecast,
    selectLocation,
  };
};
