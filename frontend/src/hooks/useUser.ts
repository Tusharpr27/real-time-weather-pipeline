import { useCallback } from 'react';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { setUser, setPreferences, logout } from '@/store/slices/userSlice';

export const useUser = () => {
  const dispatch = useAppDispatch();
  const user = useAppSelector((state) => state.user);

  const setUserData = useCallback(
    (userData: any) => {
      dispatch(setUser(userData));
    },
    [dispatch]
  );

  const updatePreferences = useCallback(
    (prefs: any) => {
      dispatch(setPreferences(prefs));
    },
    [dispatch]
  );

  const logoutUser = useCallback(() => {
    dispatch(logout());
  }, [dispatch]);

  return {
    ...user,
    setUserData,
    updatePreferences,
    logoutUser,
  };
};
