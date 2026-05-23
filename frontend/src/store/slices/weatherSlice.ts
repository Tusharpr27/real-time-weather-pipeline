import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { WeatherData } from '@/types';
import api from '@/services/api';

export interface WeatherState {
  current: WeatherData | null;
  forecast: WeatherData[];
  locations: any[];
  loading: boolean;
  error: string | null;
  lastUpdated: string | null;
  selectedLocation: string | null;
}

const initialState: WeatherState = {
  current: null,
  forecast: [],
  locations: [],
  loading: false,
  error: null,
  lastUpdated: null,
  selectedLocation: null,
};

export const fetchCurrentWeather = createAsyncThunk(
  'weather/fetchCurrent',
  async (locationId: string, { rejectWithValue }) => {
    try {
      const response = await api.getWeatherCurrent(locationId);
      return response; // api returns response.data already
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch weather');
    }
  }
);

export const fetchWeatherForecast = createAsyncThunk(
  'weather/fetchForecast',
  async (locationId: string, { rejectWithValue }) => {
    try {
      const response = await api.getWeatherForecast(locationId);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch forecast');
    }
  }
);

const weatherSlice = createSlice({
  name: 'weather',
  initialState,
  reducers: {
    setSelectedLocation: (state, action: PayloadAction<string>) => {
      state.selectedLocation = action.payload;
    },
    clearWeatherError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchCurrentWeather.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCurrentWeather.fulfilled, (state, action) => {
        state.loading = false;
        state.current = action.payload;
        state.lastUpdated = new Date().toISOString();
      })
      .addCase(fetchCurrentWeather.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      .addCase(fetchWeatherForecast.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchWeatherForecast.fulfilled, (state, action) => {
        state.loading = false;
        state.forecast = action.payload;
        state.lastUpdated = new Date().toISOString();
      })
      .addCase(fetchWeatherForecast.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { setSelectedLocation, clearWeatherError } = weatherSlice.actions;
export default weatherSlice.reducer;
