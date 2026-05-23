import { useCallback } from 'react';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import {
  fetchAlerts,
  acknowledgeAlert,
  resolveAlert,
  setFilter,
  setPage,
} from '@/store/slices/alertsSlice';

export const useAlerts = () => {
  const dispatch = useAppDispatch();
  const alerts = useAppSelector((state) => state.alerts);

  const getAlerts = useCallback(
    (params?: Record<string, any>) => {
      dispatch(fetchAlerts(params || {}));
    },
    [dispatch]
  );

  const acknowledge = useCallback(
    (alertId: string) => {
      return dispatch(acknowledgeAlert(alertId)) as any;
    },
    [dispatch]
  );

  const resolve = useCallback(
    (alertId: string) => {
      return dispatch(resolveAlert(alertId)) as any;
    },
    [dispatch]
  );

  const updateFilter = useCallback(
    (filter: Partial<typeof alerts.filter>) => {
      dispatch(setFilter(filter));
    },
    [dispatch]
  );

  const changePage = useCallback(
    (page: number) => {
      dispatch(setPage(page));
    },
    [dispatch]
  );

  return {
    ...alerts,
    getAlerts,
    acknowledge,
    resolve,
    updateFilter,
    changePage,
  };
};
