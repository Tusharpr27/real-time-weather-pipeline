export { default as weatherReducer } from './weatherSlice';
export { fetchCurrentWeather, fetchWeatherForecast, setSelectedLocation } from './weatherSlice';
export type { WeatherState } from './weatherSlice';

export { default as alertsReducer } from './alertsSlice';
export { fetchAlerts, acknowledgeAlert, resolveAlert, setFilter, setPage } from './alertsSlice';
export type { AlertsState } from './alertsSlice';

export { default as userReducer } from './userSlice';
export { setUser, setPreferences, logout } from './userSlice';
export type { UserState } from './userSlice';

export { default as uiReducer } from './uiSlice';
export {
  toggleSidebar,
  setSidebarOpen,
  toggleMobileMenu,
  setMobileMenuOpen,
  setLoading,
  addNotification,
  removeNotification,
  clearNotifications,
} from './uiSlice';
export type { UIState } from './uiSlice';
