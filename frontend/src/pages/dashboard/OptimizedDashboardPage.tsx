import { useQuery } from '@tanstack/react-query';
import { useAuthStore } from '@/stores/useAuthStore';
import { dashboardApi, progressApi, lessonsApi, usersApi } from '@/services/api';
import { Link } from 'react-router-dom';
import { 
  BookOpenIcon, 
  ChartBarIcon, 
  ChatBubbleLeftRightIcon,
  AcademicCapIcon,
  FireIcon
} from '@heroicons/react/24/outline';

// Skeleton component for loading states
function StatCardSkeleton() {
  return (
    <div className="bg-zinc-900 border border-zinc-800 animate-pulse">
      <div className="p-5">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <div className="h-6 w-6 bg-zinc-800" />
          </div>
          <div className="ml-5 w-0 flex-1">
            <div className="h-4 bg-zinc-800 w-24 mb-2" />
            <div className="h-6 bg-zinc-800 w-12" />
          </div>
        </div>
      </div>
    </div>
  );
}

function LessonCardSkeleton() {
  return (
    <div className="flex items-center space-x-3 p-3 border border-zinc-800 animate-pulse">
      <div className="flex-shrink-0">
        <div className="h-8 w-8 bg-zinc-800" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="h-4 bg-zinc-800 w-32 mb-1" />
        <div className="h-3 bg-zinc-800 w-20" />
      </div>
      <div className="h-6 bg-zinc-800 w-16" />
    </div>
  );
}

export function OptimizedDashboardPage() {
  const { user, isAuthenticated } = useAuthStore();

  // Try combined dashboard API first
  const { data: dashboardData, isLoading: dashboardLoading, error: dashboardError } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => dashboardApi.getDashboardData(),
    staleTime: 1000 * 60 * 10,
    gcTime: 1000 * 60 * 15,
    refetchOnWindowFocus: false,
    retry: 1, // Only retry once before falling back
    enabled: !!isAuthenticated,
  });

  // Fallback to individual API calls if dashboard API fails
  const { data: progress, isLoading: progressLoading } = useQuery({
    queryKey: ['progress', 'summary'],
    queryFn: () => progressApi.getSummary(),
    staleTime: 1000 * 60 * 10,
    gcTime: 1000 * 60 * 15,
    enabled: !!isAuthenticated && !!dashboardError,
    retry: 1,
  });

  const { data: lessons, isLoading: lessonsLoading } = useQuery({
    queryKey: ['lessons', 'recent'],
    queryFn: () => lessonsApi.getAll({ limit: 3 }),
    staleTime: 1000 * 60 * 10,
    gcTime: 1000 * 60 * 15,
    enabled: !!isAuthenticated && !!dashboardError,
    retry: 1,
  });

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['user-stats'],
    queryFn: () => usersApi.getStats(),
    staleTime: 1000 * 60 * 10,
    gcTime: 1000 * 60 * 15,
    enabled: !!isAuthenticated && !!dashboardError,
    retry: 1,
  });

  // Determine loading state — also covers the single-frame gap where
  // dashboardError just became truthy but fallback queries haven't started yet.
  const isDashboardSettled = !!dashboardData || !!dashboardError;
  const isFallbackLoading = !!dashboardError && (progressLoading || lessonsLoading || statsLoading);
  const isLoading = !isDashboardSettled || isFallbackLoading;

  // Use dashboard data if available, otherwise use individual API data.
  // Never fall back to hardcoded placeholder data — show an empty list instead.
  const progressData = dashboardData?.data?.progress || progress?.data || { completed_lessons: 0, total_lessons: 0, current_streak: 0 };
  const recentLessonsData: any[] = dashboardData?.data?.recent_lessons || lessons?.slice(0, 3) || [];
  const statsData = dashboardData?.data?.stats || stats?.data || { completed_lessons: 0, total_lessons: 0, current_streak: 0 };
  
  const completionRate = (progressData as any)?.total_lessons > 0
    ? Math.round(((progressData as any).completed_lessons / (progressData as any).total_lessons) * 100)
    : 0;
  const streak = (statsData as any)?.current_streak || (progressData as any)?.current_streak || 0;
  const totalLessons = (statsData as any)?.total_lessons || (progressData as any)?.total_lessons || 5;

  // Show error state only if authentication fails or there's a critical error
  const hasError = !isAuthenticated && dashboardError;
  
  if (hasError && !isLoading) {
    console.error('Dashboard API Error:', dashboardError);
    return (
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="text-center py-12">
          <div className="mx-auto h-12 w-12 text-zinc-600">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h3 className="mt-2 text-sm font-medium text-white">Unable to load dashboard</h3>
          <p className="mt-1 text-sm text-zinc-500">There was an error loading your dashboard data.</p>
          <p className="mt-1 text-xs text-zinc-600">Error: {(dashboardError as any)?.message || 'Unknown error'}</p>
          <div className="mt-6">
            <button
              onClick={() => window.location.reload()}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-bold uppercase tracking-widest text-white bg-orange-500 hover:bg-orange-400"
            >
              Refresh Page
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-black tracking-tight text-white uppercase">
          Welcome back, {user?.name || dashboardData?.data?.user_info?.name}
        </h1>
        <p className="mt-1 text-sm text-zinc-500">
          Here's your art learning journey.
        </p>
      </div>

      {/* Stats Grid - Single loading state for all stats */}
      <div className="mb-8 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {isLoading ? (
          // Show skeleton for all cards while loading
          Array.from({ length: 4 }).map((_, i) => (
            <StatCardSkeleton key={i} />
          ))
        ) : (
          <>
            <div className="bg-zinc-900 border border-zinc-800">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <AcademicCapIcon className="h-6 w-6 text-orange-500" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-xs font-semibold text-zinc-500 uppercase tracking-widest truncate">
                        Lessons Completed
                      </dt>
                      <dd className="text-2xl font-black text-white">
                      {(progressData as any)?.completed_lessons || (statsData as any)?.completed_lessons || 0}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-zinc-900 border border-zinc-800">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <ChartBarIcon className="h-6 w-6 text-orange-500" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-xs font-semibold text-zinc-500 uppercase tracking-widest truncate">
                        Completion Rate
                      </dt>
                      <dd className="text-2xl font-black text-white">
                        {completionRate}%
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-zinc-900 border border-zinc-800">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <FireIcon className="h-6 w-6 text-orange-500" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-xs font-semibold text-zinc-500 uppercase tracking-widest truncate">
                        Current Streak
                      </dt>
                      <dd className="text-2xl font-black text-white">
                        {streak} days
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-zinc-900 border border-zinc-800">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <BookOpenIcon className="h-6 w-6 text-orange-500" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-xs font-semibold text-zinc-500 uppercase tracking-widest truncate">
                        Total Lessons
                      </dt>
                      <dd className="text-2xl font-black text-white">
                        {totalLessons}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </div>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
        {/* Recent Lessons */}
        <div className="bg-zinc-900 border border-zinc-800 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-black uppercase tracking-widest text-white">Recent Lessons</h3>
            <Link 
              to="/lessons" 
              className="text-xs font-semibold text-orange-500 hover:text-orange-400 uppercase tracking-widest transition-colors"
            >
              View all →
            </Link>
          </div>
          
          <div className="space-y-2">
            {isLoading ? (
              Array.from({ length: 3 }).map((_, i) => (
                <LessonCardSkeleton key={i} />
              ))
            ) : recentLessonsData.length > 0 ? (
              recentLessonsData.map((lesson: any) => (
                <div key={lesson.id} className="flex items-center space-x-3 p-3 border border-zinc-800 hover:border-zinc-700 hover:bg-zinc-800 transition-colors">
                  <div className="flex-shrink-0">
                    <div className="h-8 w-8 bg-zinc-800 border border-zinc-700 flex items-center justify-center">
                      <BookOpenIcon className="h-5 w-5 text-orange-500" />
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-white truncate">
                      {lesson.title}
                    </p>
                    <p className="text-xs text-zinc-500 truncate">
                      {lesson.difficulty} · {lesson.duration_minutes || lesson.duration} min
                    </p>
                  </div>
                  <Link
                    to={`/lessons/${lesson.id}`}
                    className="inline-flex items-center px-2.5 py-1.5 text-xs font-bold uppercase tracking-widest text-orange-400 border border-zinc-700 hover:border-orange-500 hover:text-orange-300 transition-colors"
                  >
                    Open
                  </Link>
                </div>
              ))
            ) : (
              <div className="text-center py-6">
                <BookOpenIcon className="mx-auto h-10 w-10 text-zinc-700" />
                <h3 className="mt-2 text-sm font-semibold text-white">No lessons yet</h3>
                <p className="mt-1 text-sm text-zinc-500">Get started with your first art lesson.</p>
                <div className="mt-6">
                  <Link
                    to="/lessons"
                    className="inline-flex items-center px-4 py-2 text-sm font-bold uppercase tracking-widest text-white bg-orange-500 hover:bg-orange-400 transition-colors"
                  >
                    Browse Lessons
                  </Link>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-zinc-900 border border-zinc-800 p-6">
          <h3 className="text-sm font-black uppercase tracking-widest text-white mb-4">Quick Actions</h3>
          <div className="space-y-2">
            <Link
              to="/lessons"
              className="flex items-center p-3 border border-zinc-800 hover:border-zinc-700 hover:bg-zinc-800 transition-colors"
            >
              <div className="flex-shrink-0">
                <div className="h-8 w-8 bg-zinc-800 border border-zinc-700 flex items-center justify-center">
                  <BookOpenIcon className="h-5 w-5 text-blue-400" />
                </div>
              </div>
              <div className="ml-3">
                <p className="text-sm font-semibold text-white">Browse Lessons</p>
                <p className="text-xs text-zinc-500">Explore techniques and tutorials</p>
              </div>
            </Link>

            <Link
              to="/tutor"
              className="flex items-center p-3 border border-zinc-800 hover:border-zinc-700 hover:bg-zinc-800 transition-colors"
            >
              <div className="flex-shrink-0">
                <div className="h-8 w-8 bg-zinc-800 border border-zinc-700 flex items-center justify-center">
                  <ChatBubbleLeftRightIcon className="h-5 w-5 text-green-400" />
                </div>
              </div>
              <div className="ml-3">
                <p className="text-sm font-semibold text-white">AI Tutor</p>
                <p className="text-xs text-zinc-500">Get personalized art guidance</p>
              </div>
            </Link>

            <Link
              to="/progress"
              className="flex items-center p-3 border border-zinc-800 hover:border-zinc-700 hover:bg-zinc-800 transition-colors"
            >
              <div className="flex-shrink-0">
                <div className="h-8 w-8 bg-zinc-800 border border-zinc-700 flex items-center justify-center">
                  <ChartBarIcon className="h-5 w-5 text-purple-400" />
                </div>
              </div>
              <div className="ml-3">
                <p className="text-sm font-semibold text-white">View Progress</p>
                <p className="text-xs text-zinc-500">Track your learning journey</p>
              </div>
            </Link>
          </div>
        </div>
      </div>

      {/* Daily Learning Streak */}
      {streak > 0 && (
        <div className="mt-8 border-l-4 border-orange-500 bg-zinc-900 border border-zinc-800 p-6">
          <div className="flex items-center">
            <FireIcon className="h-8 w-8 text-orange-500" />
            <div className="ml-4">
              <h3 className="text-base font-black uppercase tracking-widest text-white">{streak} Day Streak</h3>
              <p className="text-sm text-zinc-400">
                You've been learning for {streak} days in a row. Keep it up!
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}