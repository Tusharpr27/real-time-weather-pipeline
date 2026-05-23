// Weather Data Types
export interface WeatherData {
  id: string
  location_id: string
  location: string
  temperature: number
  feels_like: number
  humidity: number
  wind_speed: number
  wind_direction: number
  pressure: number
  precipitation: number
  visibility: number
  uv_index: number
  weather_condition: string
  weather_description: string
  cloud_coverage: number
  timestamp: string
  created_at: string
  updated_at: string
}

// Alert Types
export type AlertSeverity = 'LOW' | 'MEDIUM' | 'HIGH'
export type AlertStatus = 'ACTIVE' | 'ACKNOWLEDGED' | 'RESOLVED'

export interface Alert {
  id: string
  location_id: string
  location: string
  alert_type: string
  severity: AlertSeverity
  status: AlertStatus
  message: string
  threshold: number
  current_value: number
  metric_name: string
  triggered_at: string
  acknowledged_at?: string
  resolved_at?: string
  acknowledged_by?: string
  resolution_notes?: string
  escalation_count: number
  created_at: string
  updated_at: string
}

// Location Types
export interface Location {
  id: string
  name: string
  latitude: number
  longitude: number
  country: string
  timezone: string
  is_active: boolean
  created_at: string
  updated_at: string
}

// Monitoring Types
export interface PerformanceMetrics {
  endpoint: string
  method: string
  count: number
  avg_response_time: number
  min_response_time: number
  max_response_time: number
  p95_response_time: number
  p99_response_time: number
  error_count: number
  error_rate: number
  timestamp: string
}

export interface SystemHealth {
  status: 'HEALTHY' | 'DEGRADED' | 'UNHEALTHY'
  database: ComponentHealth
  cache: ComponentHealth
  webhooks: ComponentHealth
  websocket: ComponentHealth
  timestamp: string
}

export interface ComponentHealth {
  status: 'HEALTHY' | 'UNHEALTHY'
  response_time: number
  last_checked: string
  message: string
}

// Statistics Types
export interface WeatherStatistics {
  location: string
  period: 'hourly' | 'daily' | 'weekly'
  avg_temperature: number
  max_temperature: number
  min_temperature: number
  avg_humidity: number
  avg_wind_speed: number
  avg_pressure: number
  total_precipitation: number
  conditions: Map<string, number>
  timestamp: string
}

// User Preferences
export interface UserPreferences {
  user_id: string
  temperature_unit: 'celsius' | 'fahrenheit'
  wind_speed_unit: 'kmh' | 'mph'
  pressure_unit: 'mb' | 'inHg'
  theme: 'light' | 'dark' | 'auto'
  notifications_enabled: boolean
  alert_email: string
  quiet_hours_enabled: boolean
  quiet_hours_start: string
  quiet_hours_end: string
  default_locations: string[]
  created_at: string
  updated_at: string
}

// Pagination
export interface PaginationMeta {
  page: number
  per_page: number
  total: number
  total_pages: number
}

export interface PaginatedResponse<T> {
  data: T[]
  pagination: PaginationMeta
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
  message?: string
  timestamp: string
}

export interface ApiError {
  status: number
  message: string
  details?: Record<string, unknown>
}

// Redux Store Types
export interface WeatherState {
  data: WeatherData[]
  loading: boolean
  error: string | null
  selectedLocation: string | null
}

export interface AlertsState {
  data: Alert[]
  activeAlerts: Alert[]
  loading: boolean
  error: string | null
  filter: AlertFilter
}

export interface AlertFilter {
  severity?: AlertSeverity
  status?: AlertStatus
  location_id?: string
  dateRange?: [string, string]
}

export interface UserState {
  preferences: UserPreferences | null
  loading: boolean
  error: string | null
  authenticated: boolean
}

export interface UIState {
  sidebarOpen: boolean
  theme: 'light' | 'dark'
  notifications: Notification[]
  loading: boolean
}

export interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  message: string
  duration?: number
  timestamp: string
}

// Dashboard Types
export interface DashboardData {
  currentWeather: WeatherData[]
  activeAlerts: Alert[]
  systemHealth: SystemHealth
  performanceMetrics: PerformanceMetrics[]
  statistics: WeatherStatistics[]
}

// Chart Data Types
export interface ChartDataPoint {
  label: string
  value: number
  timestamp: string
}

export interface ChartDataset {
  label: string
  data: ChartDataPoint[]
  borderColor: string
  backgroundColor: string
  fill?: boolean
}
