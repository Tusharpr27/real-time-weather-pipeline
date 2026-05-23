import { useCallback } from 'react';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import {
  toggleSidebar,
  setSidebarOpen,
  toggleMobileMenu,
  setMobileMenuOpen,
  setLoading,
  addNotification,
  removeNotification,
  clearNotifications,
} from '@/store/slices/uiSlice';

export const useUI = () => {
  const dispatch = useAppDispatch();
  const ui = useAppSelector((state) => state.ui);

  const toggleSidebarMenu = useCallback(() => {
    dispatch(toggleSidebar());
  }, [dispatch]);

  const setSidebar = useCallback(
    (open: boolean) => {
      dispatch(setSidebarOpen(open));
    },
    [dispatch]
  );

  const toggleMobileNav = useCallback(() => {
    dispatch(toggleMobileMenu());
  }, [dispatch]);

  const setMobileMenu = useCallback(
    (open: boolean) => {
      dispatch(setMobileMenuOpen(open));
    },
    [dispatch]
  );

  const setModuleLoading = useCallback(
    (key: string, loading: boolean) => {
      dispatch(setLoading({ key: key as any, value: loading }));
    },
    [dispatch]
  );

  const showNotification = useCallback(
    (notification: {
      type: 'success' | 'error' | 'warning' | 'info';
      message: string;
      duration?: number;
    }) => {
      dispatch(addNotification(notification));
    },
    [dispatch]
  );

  const hideNotification = useCallback(
    (id: string) => {
      dispatch(removeNotification(id));
    },
    [dispatch]
  );

  const clearAllNotifications = useCallback(() => {
    dispatch(clearNotifications());
  }, [dispatch]);

  return {
    ...ui,
    toggleSidebarMenu,
    setSidebar,
    toggleMobileNav,
    setMobileMenu,
    setModuleLoading,
    showNotification,
    hideNotification,
    clearAllNotifications,
  };
};
