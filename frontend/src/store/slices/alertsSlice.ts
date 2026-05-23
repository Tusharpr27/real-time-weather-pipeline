import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { Alert } from '@/types';
import api from '@/services/api';

export interface AlertsState {
  items: Alert[];
  activeCount: number;
  loading: boolean;
  error: string | null;
  filter: {
    status: 'ALL' | 'ACTIVE' | 'ACKNOWLEDGED' | 'RESOLVED';
    severity: 'ALL' | 'LOW' | 'MEDIUM' | 'HIGH';
  };
  pagination: {
    page: number;
    pageSize: number;
    total: number;
  };
}

const initialState: AlertsState = {
  items: [],
  activeCount: 0,
  loading: false,
  error: null,
  filter: {
    status: 'ALL',
    severity: 'ALL',
  },
  pagination: {
    page: 1,
    pageSize: 10,
    total: 0,
  },
};

export const fetchAlerts = createAsyncThunk(
  'alerts/fetchAlerts',
  async (
    params: {
      page?: number;
      pageSize?: number;
      status?: string;
      severity?: string;
    },
    { rejectWithValue }
  ) => {
    try {
      const response = await api.getActiveAlerts(params as any);
      // backend returns { status: 'success', count: N, alerts: [...] }
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch alerts');
    }
  }
);

export const acknowledgeAlert = createAsyncThunk(
  'alerts/acknowledge',
  async (alertId: string, { rejectWithValue, dispatch }) => {
    try {
      const response = await api.acknowledgeAlert(alertId);
      // Refresh alerts after acknowledgement
      dispatch(fetchAlerts({}));
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to acknowledge alert');
    }
  }
);

export const resolveAlert = createAsyncThunk(
  'alerts/resolve',
  async (alertId: string, { rejectWithValue, dispatch }) => {
    try {
      const response = await api.resolveAlert(alertId);
      // Refresh alerts after resolving
      dispatch(fetchAlerts({}));
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to resolve alert');
    }
  }
);

const alertsSlice = createSlice({
  name: 'alerts',
  initialState,
  reducers: {
    setFilter: (state, action: PayloadAction<Partial<AlertsState['filter']>>) => {
      state.filter = { ...state.filter, ...action.payload };
      state.pagination.page = 1;
    },
    setPage: (state, action: PayloadAction<number>) => {
      state.pagination.page = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchAlerts.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAlerts.fulfilled, (state, action: PayloadAction<any>) => {
        state.loading = false;
        // backend returns { status: 'success', count, alerts }
        state.items = action.payload.alerts || [];
        state.pagination.total = action.payload.count || (action.payload.alerts || []).length;
        state.activeCount = action.payload.count || (action.payload.alerts || []).length;
      })
      .addCase(fetchAlerts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      .addCase(acknowledgeAlert.fulfilled, (state, action: PayloadAction<Alert>) => {
        const index = state.items.findIndex((a) => a.id === action.payload.id);
        if (index !== -1) {
          state.items[index] = action.payload;
        }
      })
      .addCase(resolveAlert.fulfilled, (state, action: PayloadAction<Alert>) => {
        const index = state.items.findIndex((a) => a.id === action.payload.id);
        if (index !== -1) {
          state.items[index] = action.payload;
        }
      });
  },
});

export const { setFilter, setPage, clearError } = alertsSlice.actions;
export default alertsSlice.reducer;
