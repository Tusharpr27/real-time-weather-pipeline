import api from './api';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    name: string;
    avatar_url?: string;
  };
}

export interface RegisterRequest {
  email: string;
  name: string;
  password: string;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetConfirmRequest {
  token: string;
  password: string;
}

export interface UserProfile {
  id: string;
  email: string;
  name: string;
  avatar_url?: string;
  bio?: string;
  location?: string;
  phone?: string;
  created_at: string;
  updated_at: string;
}

export interface UserPreferences {
  user_id: string;
  theme: 'light' | 'dark' | 'system';
  emailNotifications: boolean;
  weatherAlerts: boolean;
  alertSummary: 'immediate' | 'daily' | 'weekly' | 'never';
  temperatureUnit: 'celsius' | 'fahrenheit';
  windSpeedUnit: 'ms' | 'kmh' | 'mph' | 'knots';
  language: 'en' | 'es' | 'fr' | 'de';
}

class AuthService {
  /**
   * Login with email and password
   */
  async login(request: LoginRequest): Promise<LoginResponse> {
    const response = await api.client.post<LoginResponse>('/auth/login', request);
    const token = response.data?.access_token;
    if (token) {
      // Keep api client in sync and persist token under unified key
      if (typeof api.setAuthToken === 'function') api.setAuthToken(token as string);
      localStorage.setItem('auth_token', token as string);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  }

  /**
   * Register new user
   */
  async register(request: RegisterRequest): Promise<LoginResponse> {
    const response = await api.client.post<LoginResponse>('/auth/register', request);
    const token = response.data?.access_token;
    if (token) {
      if (typeof api.setAuthToken === 'function') api.setAuthToken(token as string);
      localStorage.setItem('auth_token', token as string);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  }

  /**
   * Request password reset
   */
  async requestPasswordReset(request: PasswordResetRequest): Promise<{ message: string }> {
    return (await api.client.post<{ message: string }>('/auth/password-reset', request)).data;
  }

  /**
   * Confirm password reset with token
   */
  async confirmPasswordReset(request: PasswordResetConfirmRequest): Promise<{ message: string }> {
    return (await api.client.post<{ message: string }>('/auth/password-reset/confirm', request)).data;
  }

  /**
   * Get current user profile
   */
  async getProfile(): Promise<UserProfile> {
    try {
      const response = await api.client.get<any>('/auth/me');
      const backendUser = response.data;
      return {
        id: String(backendUser.id),
        email: backendUser.email,
        name: backendUser.full_name || 'Showcase User',
        created_at: backendUser.created_at || new Date().toISOString(),
        updated_at: backendUser.created_at || new Date().toISOString(),
        location: 'Delhi',
        phone: '',
        bio: 'Showcase user profile',
      };
    } catch (e) {
      const stored = localStorage.getItem('user');
      if (stored) {
        const parsed = JSON.parse(stored);
        return {
          id: parsed.id || '1',
          email: parsed.email || 'user@example.com',
          name: parsed.full_name || parsed.name || 'Showcase User',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          location: 'Delhi',
          phone: '',
          bio: 'Showcase user profile',
        };
      }
      return {
        id: '1',
        email: 'user@example.com',
        name: 'Showcase User',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        location: 'Delhi',
        phone: '',
        bio: 'Showcase user profile',
      };
    }
  }

  /**
   * Update user profile
   */
  async updateProfile(profile: Partial<UserProfile>): Promise<UserProfile> {
    const stored = localStorage.getItem('user');
    let currentUser = stored ? JSON.parse(stored) : {};
    const updatedUser = { ...currentUser, ...profile, full_name: profile.name || currentUser.full_name || profile.fullName };
    localStorage.setItem('user', JSON.stringify(updatedUser));
    return {
      id: updatedUser.id || '1',
      email: updatedUser.email || 'user@example.com',
      name: updatedUser.full_name || 'Showcase User',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      location: updatedUser.location || 'Delhi',
      phone: updatedUser.phone || '',
      bio: updatedUser.bio || '',
    };
  }

  /**
   * Change password
   */
  async changePassword(
    currentPassword: string,
    newPassword: string
  ): Promise<{ message: string }> {
    return (
      await api.client.post<{ message: string }>('/auth/change-password', {
        old_password: currentPassword,
        new_password: newPassword,
      })
    ).data;
  }

  /**
   * Get user preferences
   */
  async getPreferences(): Promise<UserPreferences> {
    const stored = localStorage.getItem('preferences');
    if (stored) {
      return JSON.parse(stored);
    }
    const defaultPrefs: UserPreferences = {
      user_id: '1',
      theme: 'dark',
      emailNotifications: true,
      weatherAlerts: true,
      alertSummary: 'immediate',
      temperatureUnit: 'celsius',
      windSpeedUnit: 'kmh',
      language: 'en',
    };
    localStorage.setItem('preferences', JSON.stringify(defaultPrefs));
    return defaultPrefs;
  }

  /**
   * Update user preferences
   */
  async updatePreferences(preferences: Partial<UserPreferences>): Promise<UserPreferences> {
    const stored = localStorage.getItem('preferences');
    let currentPrefs = stored ? JSON.parse(stored) : {
      user_id: '1',
      theme: 'dark',
      emailNotifications: true,
      weatherAlerts: true,
      alertSummary: 'immediate',
      temperatureUnit: 'celsius',
      windSpeedUnit: 'kmh',
      language: 'en',
    };
    const updatedPrefs = { ...currentPrefs, ...preferences };
    localStorage.setItem('preferences', JSON.stringify(updatedPrefs));
    return updatedPrefs;
  }

  /**
   * Logout user
   */
  logout(): void {
    if (typeof api.clearAuthToken === 'function') api.clearAuthToken();
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    localStorage.removeItem('preferences');
  }

  /**
   * Get stored token
   */
  getToken(): string | null {
    return localStorage.getItem('auth_token');
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  /**
   * Get stored user from localStorage
   */
  getStoredUser(): any {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  }
}

export default new AuthService();
