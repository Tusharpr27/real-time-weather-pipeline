import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import api from '@/services/api';

export interface ChartData {
  timestamp: string;
  temperature?: number;
  humidity?: number;
  pressure?: number;
  windSpeed?: number;
  precipitation?: number;
}

export interface ChartsState {
  temperatureData: ChartData[];
  humidityData: ChartData[];
  pressureData: ChartData[];
  windData: ChartData[];
  precipitationData: ChartData[];
  selectedTimeRange: '24h' | '7d' | '30d' | '90d' | '1y';
  loading: boolean;
  error: string | null;
}

const initialState: ChartsState = {
  temperatureData: [],
  humidityData: [],
  pressureData: [],
  windData: [],
  precipitationData: [],
  selectedTimeRange: '24h',
  loading: false,
  error: null,
};

export const fetchChartData = createAsyncThunk(
  'charts/fetchChartData',
  async (
    params: {
      timeRange: string;
      location?: string;
    },
    { rejectWithValue }
  ) => {
    try {
      const response = await api.getHistoricalData(params);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.detail || 'Failed to fetch chart data'
      );
    }
  }
);

const chartsSlice = createSlice({
  name: 'charts',
  initialState,
  reducers: {
    setTimeRange: (state, action: PayloadAction<'24h' | '7d' | '30d' | '90d' | '1y'>) => {
      state.selectedTimeRange = action.payload;
    },
    clearChartData: (state) => {
      state.temperatureData = [];
      state.humidityData = [];
      state.pressureData = [];
      state.windData = [];
      state.precipitationData = [];
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchChartData.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchChartData.fulfilled, (state, action: PayloadAction<any>) => {
        state.loading = false;
        state.temperatureData = action.payload.temperature || [];
        state.humidityData = action.payload.humidity || [];
        state.pressureData = action.payload.pressure || [];
        state.windData = action.payload.wind || [];
        state.precipitationData = action.payload.precipitation || [];
      })
      .addCase(fetchChartData.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { setTimeRange, clearChartData } = chartsSlice.actions;
export default chartsSlice.reducer;
