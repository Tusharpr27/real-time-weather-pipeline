import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface UIState {
  sidebarOpen: boolean;
  mobileMenuOpen: boolean;
  loading: {
    dashboard: boolean;
    alerts: boolean;
    weather: boolean;
  };
  notifications: Array<{
    id: string;
    type: 'success' | 'error' | 'warning' | 'info';
    message: string;
    duration?: number;
  }>;
}

const initialState: UIState = {
  sidebarOpen: true,
  mobileMenuOpen: false,
  loading: {
    dashboard: false,
    alerts: false,
    weather: false,
  },
  notifications: [],
};

let notificationId = 0;

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    setSidebarOpen: (state, action: PayloadAction<boolean>) => {
      state.sidebarOpen = action.payload;
    },
    toggleMobileMenu: (state) => {
      state.mobileMenuOpen = !state.mobileMenuOpen;
    },
    setMobileMenuOpen: (state, action: PayloadAction<boolean>) => {
      state.mobileMenuOpen = action.payload;
    },
    setLoading: (
      state,
      action: PayloadAction<{ key: keyof UIState['loading']; value: boolean }>
    ) => {
      state.loading[action.payload.key] = action.payload.value;
    },
    addNotification: (
      state,
      action: PayloadAction<{
        type: 'success' | 'error' | 'warning' | 'info';
        message: string;
        duration?: number;
      }>
    ) => {
      state.notifications.push({
        id: `notification-${notificationId++}`,
        ...action.payload,
      });
    },
    removeNotification: (state, action: PayloadAction<string>) => {
      state.notifications = state.notifications.filter(
        (n) => n.id !== action.payload
      );
    },
    clearNotifications: (state) => {
      state.notifications = [];
    },
  },
});

export const {
  toggleSidebar,
  setSidebarOpen,
  toggleMobileMenu,
  setMobileMenuOpen,
  setLoading,
  addNotification,
  removeNotification,
  clearNotifications,
} = uiSlice.actions;

export default uiSlice.reducer;
