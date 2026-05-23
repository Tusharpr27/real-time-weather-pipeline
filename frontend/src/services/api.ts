import axios, { AxiosInstance, AxiosError } from 'axios'
import type {
  WeatherData,
  Alert,
  Location,
  PerformanceMetrics,
  SystemHealth,
  PaginatedResponse,
  ApiResponse,
  ApiError,
} from '@types'

const apiURL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
const cleanedBaseURL = apiURL.replace(/\/api\/?$/, '')

// Create a shared axios instance for both internal and external use
const axiosInstance = axios.create({
  baseURL: cleanedBaseURL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

class APIClient {
  public client: AxiosInstance

  constructor(baseURL: string = import.meta.env.VITE_API_URL || 'http://localhost:8000/api') {
    this.client = axiosInstance

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        if (config.url && config.url.startsWith('/') && !config.url.startsWith('/api')) {
          config.url = `/api${config.url}`
        }
        const token = localStorage.getItem('auth_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Handle unauthorized - redirect to login
          localStorage.removeItem('auth_token')
          // No auth redirect for showcase project
        }
        return Promise.reject(this.handleError(error))
      }
    )
  }

  private handleError(error: AxiosError): ApiError {
    if (error.response) {
      return {
        status: error.response.status,
        message: (error.response.data as any)?.detail || error.message,
        details: error.response.data as any,
      }
    }
    return {
      status: 500,
      message: error.message || 'An error occurred',
    }
  }

  // Authentication Endpoints
  async login(email: string, password: string) {
    const res = await this.client.post<any>('/auth/login', { email, password })
    if (res.data.access_token) {
      this.setAuthToken(res.data.access_token)
      localStorage.setItem('user', JSON.stringify(res.data.user || { email }))
    }
    return res.data
  }

  async register(email: string, password: string, fullName: string) {
    const res = await this.client.post<any>('/auth/register', { 
      email, 
      password, 
      full_name: fullName 
    })
    if (res.data.access_token) {
      this.setAuthToken(res.data.access_token)
      localStorage.setItem('user', JSON.stringify(res.data.user || { email, full_name: fullName }))
    }
    return res.data
  }

  async getMe() {
    const res = await this.client.get<any>('/auth/me')
    return res.data
  }

  async logout() {
    try {
      await this.client.post('/auth/logout', {})
    } finally {
      this.clearAuthToken()
      localStorage.removeItem('user')
    }
  }

  async refreshToken() {
    const res = await this.client.post<any>('/auth/refresh-token', {})
    if (res.data.access_token) {
      this.setAuthToken(res.data.access_token)
    }
    return res.data
  }

  async changePassword(currentPassword: string, newPassword: string) {
    const res = await this.client.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    })
    return res.data
  }

  // Health & Status
  async getHealth() {
    const res = await this.client.get<ApiResponse<any>>('/health')
    return res.data
  }

  // Weather Endpoints
  async getWeatherCurrent(location: string) {
    const res = await this.client.get<WeatherData>(`/weather/current/${location}`)
    return res.data
  }

  async getWeatherHistory(location: string, limit: number = 100) {
    const res = await this.client.get<PaginatedResponse<WeatherData>>(`/weather/history/${location}`, {
      params: { limit },
    })
    return res.data
  }

  async getWeatherForecast(location: string, days: number = 7) {
    const res = await this.client.get<WeatherData[]>(`/weather/history/${location}`, {
      params: { days },
    })
    return res.data
  }

  async getWeatherStats(location: string) {
    const res = await this.client.get<any>(`/weather/stats/${location}`)
    return res.data
  }

  async getLocations() {
    const res = await this.client.get<Location[]>(`/weather/locations`)
    return res.data
  }

  // Alert Endpoints
  // Alert Endpoints (backend implements alerts under /api/alerts)
  async getActiveAlerts(params?: { location_id?: number; page?: number; pageSize?: number }) {
    const res = await this.client.get<any>('/alerts/active', { params });
    return res.data;
  }

  async getAlertStatistics() {
    const res = await this.client.get<any>('/alerts/statistics');
    return res.data;
  }

  async getLocationAlerts(location: string) {
    const res = await this.client.get<Alert[]>(`/alerts/active`, { params: { location_id: location } });
    return res.data;
  }

  async acknowledgeAlert(alertId: string, notes?: string) {
    const res = await this.client.post<any>(`/alerts/acknowledge/${alertId}`, { notes });
    return res.data;
  }

  async resolveAlert(alertId: string, resolution_notes?: string) {
    const res = await this.client.post<any>(`/alerts/resolve/${alertId}`, { resolution_notes });
    return res.data;
  }

  // Export Endpoints
  async exportAlerts(format: 'json' | 'csv' | 'jsonl' = 'json', limit: number = 100) {
    const res = await this.client.get(`/export/alerts`, {
      params: { format, limit },
      responseType: 'blob',
    })
    return res.data
  }

  async exportWeatherData(location: string, format: 'json' | 'csv' = 'json') {
    const res = await this.client.get(`/export/weather`, {
      params: { location_id: location, format },
      responseType: 'blob',
    })
    return res.data
  }

  // Monitoring Endpoints
  async getMonitoringMetrics() {
    const res = await this.client.get<any>('/monitoring/metrics/overview')
    return res.data
  }

  async getSystemHealth() {
    const res = await this.client.get<SystemHealth>('/monitoring/health')
    return res.data
  }

  async getErrorStats(windowSeconds: number = 3600) {
    const res = await this.client.get<any>('/monitoring/errors/overview', {
      params: { window_seconds: windowSeconds },
    })
    return res.data
  }

  async getDashboard() {
    const res = await this.client.get<any>('/monitoring/dashboard')
    return res.data
  }

  async getAuditLogs(limit: number = 100) {
    const res = await this.client.get<any>('/monitoring/audit/overview', {
      params: { limit },
    })
    return res.data
  }

  // Storage Endpoints
  async getStorageStats() {
    const res = await this.client.get<any>('/storage/stats')
    return res.data
  }

  async getArchives(limit: number = 10) {
    const res = await this.client.get<any>('/storage/archives', {
      params: { limit },
    })
    return res.data
  }

  // Settings
  setAuthToken(token: string) {
    localStorage.setItem('auth_token', token)
    this.client.defaults.headers.common.Authorization = `Bearer ${token}`
  }

  clearAuthToken() {
    localStorage.removeItem('auth_token')
    delete this.client.defaults.headers.common.Authorization
  }
}

export const apiClient = new APIClient()
export default apiClient

