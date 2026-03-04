import { useQuery } from '@tanstack/react-query';
import { useAuthStore } from '@/stores/useAuthStore';
import { progressApi, lessonsApi, usersApi } from '@/services/api';
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
    <div className="bg-white overflow-hidden shadow rounded-lg animate-pulse">
      <div className="p-5">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <div className="h-6 w-6 bg-gray-200 rounded" />
          </div>
          <div className="ml-5 w-0 flex-1">
            <div className="h-4 bg-gray-200 rounded w-24 mb-2" />
            <div className="h-6 bg-gray-200 rounded w-12" />
          </div>
        </div>
      </div>
    </div>
  );
}

function LessonCardSkeleton() {
  return (
    <div className="flex items-center space-x-3 p-3 rounded-lg border border-gray-200 animate-pulse">
      <div className="flex-shrink-0">
        <div className="h-8 w-8 bg-gray-200 rounded-lg" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="h-4 bg-gray-200 rounded w-32 mb-1" />
        <div className="h-3 bg-gray-200 rounded w-20" />
      </div>
      <div className="h-6 bg-gray-200 rounded w-16" />
    </div>
  );
}

export function DashboardPage() {
  const { user } = useAuthStore();

  // Fetch user progress with optimized caching
  const { data: progress, isLoading: progressLoading } = useQuery({
    queryKey: ['progress', 'summary'],
    queryFn: () => progressApi.getSummary(),
    staleTime: 1000 * 60 * 10, // 10 minutes - dashboard data doesn't change frequently
    gcTime: 1000 * 60 * 15, // 15 minutes
  });

  // Fetch recent lessons with optimized caching
  const { data: lessons, isLoading: lessonsLoading } = useQuery({
    queryKey: ['lessons', 'recent'],
    queryFn: () => lessonsApi.getAll({ limit: 3 }),
    staleTime: 1000 * 60 * 10, // 10 minutes
    gcTime: 1000 * 60 * 15, // 15 minutes
  });

  // Fetch user stats with optimized caching
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['user-stats'],
    queryFn: () => usersApi.getStats(),
    staleTime: 1000 * 60 * 10, // 10 minutes  
    gcTime: 1000 * 60 * 15, // 15 minutes
  });

  // Calculate derived values with fallbacks
  const recentLessons = lessons?.slice(0, 3) || [];
  const completionRate = progress?.data ? Math.round(((progress.data as any).completed_lessons / (progress.data as any).total_lessons) * 100) : 0;
  const streak = (stats?.data as any)?.current_streak || (progress?.data as any)?.current_streak || 0;
  const totalLessons = (stats?.data as any)?.total_lessons || (progress?.data as any)?.total_lessons || 0;

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome back, {user?.name}! 👋
        </h1>
        <p className="mt-1 text-sm text-gray-600">
          Here's what's happening with your art learning journey today.
        </p>
      </div>

      {/* Stats Grid - Progressive Loading */}
      <div className="mb-8 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {progressLoading || statsLoading ? (
          <StatCardSkeleton />
        ) : (
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <AcademicCapIcon className="h-6 w-6 text-gray-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Lessons Completed
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {(progress?.data as any)?.completed_lessons || (stats?.data as any)?.completed_lessons || 0}  
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        )}

        {progressLoading ? (
          <StatCardSkeleton />
        ) : (
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ChartBarIcon className="h-6 w-6 text-gray-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Completion Rate
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {Math.round(completionRate)}%
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        )}

        {progressLoading || statsLoading ? (
          <StatCardSkeleton />
        ) : (
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <FireIcon className="h-6 w-6 text-orange-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Current Streak
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {streak} days
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        )}

        {progressLoading || statsLoading ? (
          <StatCardSkeleton />
        ) : (
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <BookOpenIcon className="h-6 w-6 text-gray-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Total Lessons
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {totalLessons}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
        {/* Recent Lessons */}
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">Recent Lessons</h3>
            <Link 
              to="/lessons" 
              className="text-sm font-medium text-indigo-600 hover:text-indigo-500"
            >
              View all
            </Link>
          </div>
          
          <div className="space-y-3">
            {lessonsLoading ? (
              // Show skeleton loading state
              Array.from({ length: 3 }).map((_, i) => (
                <LessonCardSkeleton key={i} />
              ))
            ) : recentLessons.length > 0 ? (
              recentLessons.map((lesson: any) => (
                <div key={lesson.id} className="flex items-center space-x-3 p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
                  <div className="flex-shrink-0">
                    <div className="h-8 w-8 bg-indigo-100 rounded-lg flex items-center justify-center">
                      <BookOpenIcon className="h-5 w-5 text-indigo-600" />
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {lesson.title}
                    </p>
                    <p className="text-sm text-gray-500 truncate">
                      {lesson.difficulty} • {lesson.duration_minutes || lesson.duration} min
                    </p>
                  </div>
                  <Link
                    to={`/lessons/${lesson.id}`}
                    className="inline-flex items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded text-indigo-700 bg-indigo-100 hover:bg-indigo-200 transition-colors"
                  >
                    Continue
                  </Link>
                </div>
              ))
            ) : (
              <div className="text-center py-6">
                <BookOpenIcon className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No lessons yet</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Get started with your first art lesson.
                </p>
                <div className="mt-6">
                  <Link
                    to="/lessons"
                    className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 transition-colors"
                  >
                    Browse Lessons
                  </Link>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <Link
              to="/lessons"
              className="flex items-center p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
            >
              <div className="flex-shrink-0">
                <div className="h-8 w-8 bg-blue-100 rounded-lg flex items-center justify-center">
                  <BookOpenIcon className="h-5 w-5 text-blue-600" />
                </div>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900">Browse Lessons</p>
                <p className="text-sm text-gray-500">Explore art techniques and tutorials</p>
              </div>
            </Link>

            <Link
              to="/tutor"
              className="flex items-center p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
            >
              <div className="flex-shrink-0">
                <div className="h-8 w-8 bg-green-100 rounded-lg flex items-center justify-center">
                  <ChatBubbleLeftRightIcon className="h-5 w-5 text-green-600" />
                </div>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900">AI Tutor</p>
                <p className="text-sm text-gray-500">Get personalized art guidance</p>
              </div>
            </Link>

            <Link
              to="/progress"
              className="flex items-center p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
            >
              <div className="flex-shrink-0">
                <div className="h-8 w-8 bg-purple-100 rounded-lg flex items-center justify-center">
                  <ChartBarIcon className="h-5 w-5 text-purple-600" />
                </div>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900">View Progress</p>
                <p className="text-sm text-gray-500">Track your learning journey</p>
              </div>
            </Link>
          </div>
        </div>
      </div>

      {/* Daily Learning Streak */}
      {streak > 0 && (
        <div className="mt-8 bg-gradient-to-r from-orange-400 to-pink-500 rounded-lg p-6 text-white">
          <div className="flex items-center">
            <FireIcon className="h-8 w-8 text-orange-200" />
            <div className="ml-4">
              <h3 className="text-lg font-medium">🎉 Amazing streak!</h3>
              <p className="text-orange-100">
                You've been learning for {streak} days in a row. Keep it up!
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}







