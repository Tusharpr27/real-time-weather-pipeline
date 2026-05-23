import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import authService, { UserProfile, UserPreferences } from '@/services/authService';

export interface UserState {
  user: UserProfile | null;
  preferences: UserPreferences | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

const initialState: UserState = {
  user: authService.getStoredUser(),
  preferences: null,
  isAuthenticated: authService.isAuthenticated(),
  loading: false,
  error: null,
};

// Async Thunks
export const login = createAsyncThunk(
  'user/login',
  async (
    { email, password }: { email: string; password: string },
    { rejectWithValue }
  ) => {
    try {
      const response = await authService.login({ email, password });
      return { user: response.user };
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Login failed');
    }
  }
);

export const register = createAsyncThunk(
  'user/register',
  async (
    { email, name, password }: { email: string; name: string; password: string },
    { rejectWithValue }
  ) => {
    try {
      const response = await authService.register({ email, name, password });
      return { user: response.user };
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Registration failed');
    }
  }
);

export const requestPasswordReset = createAsyncThunk(
  'user/requestPasswordReset',
  async (email: string, { rejectWithValue }) => {
    try {
      await authService.requestPasswordReset({ email });
      return { email };
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Password reset request failed');
    }
  }
);

export const fetchProfile = createAsyncThunk(
  'user/fetchProfile',
  async (_, { rejectWithValue }) => {
    try {
      const profile = await authService.getProfile();
      return profile;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch profile');
    }
  }
);

export const updateProfile = createAsyncThunk(
  'user/updateProfile',
  async (profile: Partial<UserProfile>, { rejectWithValue }) => {
    try {
      const updated = await authService.updateProfile(profile);
      return updated;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to update profile');
    }
  }
);

export const changePassword = createAsyncThunk(
  'user/changePassword',
  async (
    { currentPassword, newPassword }: { currentPassword: string; newPassword: string },
    { rejectWithValue }
  ) => {
    try {
      await authService.changePassword(currentPassword, newPassword);
      return { message: 'Password changed successfully' };
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to change password');
    }
  }
);

export const fetchPreferences = createAsyncThunk(
  'user/fetchPreferences',
  async (_, { rejectWithValue }) => {
    try {
      const preferences = await authService.getPreferences();
      return preferences;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch preferences');
    }
  }
);

export const updatePreferences = createAsyncThunk(
  'user/updatePreferences',
  async (preferences: Partial<UserPreferences>, { rejectWithValue }) => {
    try {
      const updated = await authService.updatePreferences(preferences);
      return updated;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to update preferences');
    }
  }
);

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    logout: (state) => {
      authService.logout();
      state.user = null;
      state.preferences = null;
      state.isAuthenticated = false;
      state.error = null;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(login.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload.user;
        state.isAuthenticated = true;
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })

      // Register
      .addCase(register.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(register.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload.user;
        state.isAuthenticated = true;
      })
      .addCase(register.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })

      // Fetch Profile
      .addCase(fetchProfile.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchProfile.fulfilled, (state, action: PayloadAction<UserProfile>) => {
        state.loading = false;
        state.user = action.payload;
      })
      .addCase(fetchProfile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })

      // Update Profile
      .addCase(updateProfile.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateProfile.fulfilled, (state, action: PayloadAction<UserProfile>) => {
        state.loading = false;
        state.user = action.payload;
      })
      .addCase(updateProfile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })

      // Change Password
      .addCase(changePassword.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(changePassword.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(changePassword.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })

      // Fetch Preferences
      .addCase(fetchPreferences.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchPreferences.fulfilled, (state, action: PayloadAction<UserPreferences>) => {
        state.loading = false;
        state.preferences = action.payload;
      })
      .addCase(fetchPreferences.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })

      // Update Preferences
      .addCase(updatePreferences.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updatePreferences.fulfilled, (state, action: PayloadAction<UserPreferences>) => {
        state.loading = false;
        state.preferences = action.payload;
      })
      .addCase(updatePreferences.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })

      // Request Password Reset
      .addCase(requestPasswordReset.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(requestPasswordReset.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(requestPasswordReset.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { logout, clearError } = userSlice.actions;
export default userSlice.reducer;
