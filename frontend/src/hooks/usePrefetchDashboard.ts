import { useQueryClient } from '@tanstack/react-query';
import { dashboardApi } from '@/services/api';

export function usePrefetchDashboard() {
  const queryClient = useQueryClient();

  const prefetchDashboard = () => {
    queryClient.prefetchQuery({
      queryKey: ['dashboard'],
      queryFn: () => dashboardApi.getDashboardData(),
      staleTime: 1000 * 60 * 10, // 10 minutes
    });
  };

  return { prefetchDashboard };
}