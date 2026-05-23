import { useCallback } from 'react';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import {
  login,
  register,
  logout,
  fetchProfile,
  updateProfile,
  changePassword,
  fetchPreferences,
  updatePreferences,
  requestPasswordReset,
  clearError,
} from '@/store/slices/userSlice';

export const useAuth = () => {
  const dispatch = useAppDispatch();
  const user = useAppSelector((state) => state.user);

  const handleLogin = useCallback(
    async (email: string, password: string) => {
      const result = await dispatch(login({ email, password }));
      if (login.fulfilled.match(result)) {
        return result.payload;
      }
      throw new Error(result.payload);
    },
    [dispatch]
  );

  const handleRegister = useCallback(
    async (email: string, name: string, password: string) => {
      const result = await dispatch(register({ email, name, password }));
      if (register.fulfilled.match(result)) {
        return result.payload;
      }
      throw new Error(result.payload);
    },
    [dispatch]
  );

  const handleLogout = useCallback(() => {
    dispatch(logout());
  }, [dispatch]);

  const handleFetchProfile = useCallback(async () => {
    const result = await dispatch(fetchProfile());
    if (fetchProfile.fulfilled.match(result)) {
      return result.payload;
    }
    throw new Error(result.payload);
  }, [dispatch]);

  const handleUpdateProfile = useCallback(
    async (profile: any) => {
      const result = await dispatch(updateProfile(profile));
      if (updateProfile.fulfilled.match(result)) {
        return result.payload;
      }
      throw new Error(result.payload);
    },
    [dispatch]
  );

  const handleChangePassword = useCallback(
    async (currentPassword: string, newPassword: string) => {
      const result = await dispatch(
        changePassword({ currentPassword, newPassword })
      );
      if (changePassword.fulfilled.match(result)) {
        return result.payload;
      }
      throw new Error(result.payload);
    },
    [dispatch]
  );

  const handleFetchPreferences = useCallback(async () => {
    const result = await dispatch(fetchPreferences());
    if (fetchPreferences.fulfilled.match(result)) {
      return result.payload;
    }
    throw new Error(result.payload);
  }, [dispatch]);

  const handleUpdatePreferences = useCallback(
    async (preferences: any) => {
      const result = await dispatch(updatePreferences(preferences));
      if (updatePreferences.fulfilled.match(result)) {
        return result.payload;
      }
      throw new Error(result.payload);
    },
    [dispatch]
  );

  const handleRequestPasswordReset = useCallback(
    async (email: string) => {
      const result = await dispatch(requestPasswordReset(email));
      if (requestPasswordReset.fulfilled.match(result)) {
        return result.payload;
      }
      throw new Error(result.payload);
    },
    [dispatch]
  );

  const handleClearError = useCallback(() => {
    dispatch(clearError());
  }, [dispatch]);

  return {
    // State
    user: user.user,
    preferences: user.preferences,
    isAuthenticated: user.isAuthenticated,
    loading: user.loading,
    error: user.error,

    // Methods
    login: handleLogin,
    register: handleRegister,
    logout: handleLogout,
    fetchProfile: handleFetchProfile,
    updateProfile: handleUpdateProfile,
    changePassword: handleChangePassword,
    fetchPreferences: handleFetchPreferences,
    updatePreferences: handleUpdatePreferences,
    requestPasswordReset: handleRequestPasswordReset,
    clearError: handleClearError,
  };
};
