import { useEffect, lazy, Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/useAuthStore';
import { useThemeStore } from '@/stores/useThemeStore';

// Layout Components
import { AuthLayout } from '@/components/layouts/AuthLayout';
import { DashboardLayout } from '@/components/layouts/DashboardLayout';

// Components
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

// Lazy load pages for better performance
const LoginPage = lazy(() => import('@/pages/auth/LoginPage').then(m => ({ default: m.LoginPage })));
const RegisterPage = lazy(() => import('@/pages/auth/RegisterPage').then(m => ({ default: m.RegisterPage })));
const OptimizedDashboardPage = lazy(() => import('@/pages/dashboard/OptimizedDashboardPage').then(m => ({ default: m.OptimizedDashboardPage })));
const LessonsPage = lazy(() => import('@/pages/lessons/LessonsPage').then(m => ({ default: m.LessonsPage })));
const LessonDetailPage = lazy(() => import('@/pages/lessons/LessonDetailPage').then(m => ({ default: m.LessonDetailPage })));
const QuizPage = lazy(() => import('@/pages/quiz/QuizPage').then(m => ({ default: m.QuizPage })));
const ProgressPage = lazy(() => import('@/pages/progress/ProgressPage').then(m => ({ default: m.ProgressPage })));
const TutorPage = lazy(() => import('@/pages/tutor/TutorPage').then(m => ({ default: m.TutorPage })));
const ProfilePage = lazy(() => import('@/pages/profile/ProfilePage').then(m => ({ default: m.ProfilePage })));

// Eagerly preload all page chunks so navigation is instant (no "loading" flash)
function preloadAllPages() {
  import('@/pages/dashboard/OptimizedDashboardPage');
  import('@/pages/lessons/LessonsPage');
  import('@/pages/lessons/LessonDetailPage');
  import('@/pages/progress/ProgressPage');
  import('@/pages/tutor/TutorPage');
  import('@/pages/profile/ProfilePage');
  import('@/pages/quiz/QuizPage');
}

// Loading fallback
const PageLoader = () => (
  <div className="min-h-screen flex items-center justify-center bg-zinc-950">
    <div className="text-center">
      <LoadingSpinner size="lg" />
      <p className="mt-4 text-zinc-500 font-medium uppercase tracking-widest">Loading...</p>
    </div>
  </div>
);

function App() {
  const { isAuthenticated, isLoading, getCurrentUser } = useAuthStore();
  const { isDark } = useThemeStore();

  // Sync dark class with stored preference on every render
  useEffect(() => {
    document.documentElement.classList.toggle('dark', isDark);
  }, [isDark]);

  // Initialize auth state on app load
  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      getCurrentUser();
    }
    // Preload all page chunks in the background after app mounts
    // This prevents the "loading" flash when navigating between pages
    const timer = setTimeout(preloadAllPages, 500);
    return () => clearTimeout(timer);
  }, [getCurrentUser]);

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-zinc-950">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-950">
      <Suspense fallback={<PageLoader />}>
        <Routes>
          {/* Public Routes */}
          <Route
            path="/login"
            element={
              !isAuthenticated ? (
                <AuthLayout>
                  <LoginPage />
                </AuthLayout>
              ) : (
                <Navigate to="/dashboard" replace />
              )
            }
          />
          
          <Route
            path="/register"
            element={
              !isAuthenticated ? (
                <AuthLayout>
                  <RegisterPage />
                </AuthLayout>
              ) : (
                <Navigate to="/dashboard" replace />
              )
            }
          />

          {/* Protected Routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardLayout>
                  <OptimizedDashboardPage />
                </DashboardLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/lessons"
            element={
              <ProtectedRoute>
                <DashboardLayout>
                  <LessonsPage />
                </DashboardLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/lessons/:id"
            element={
              <ProtectedRoute>
                <DashboardLayout>
                  <LessonDetailPage />
                </DashboardLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/lessons/:lessonId/quiz"
            element={
              <ProtectedRoute>
                <DashboardLayout>
                  <QuizPage />
                </DashboardLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/progress"
            element={
              <ProtectedRoute>
                <DashboardLayout>
                  <ProgressPage />
                </DashboardLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/tutor"
            element={
              <ProtectedRoute>
                <DashboardLayout>
                  <TutorPage />
                </DashboardLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <DashboardLayout>
                  <ProfilePage />
                </DashboardLayout>
              </ProtectedRoute>
            }
          />

          {/* Default Redirects */}
          <Route
            path="/"
            element={
              <Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />
            }
          />

          {/* 404 Route */}
          <Route
            path="*"
            element={
              <div className="min-h-screen flex items-center justify-center bg-zinc-950">
                <div className="text-center">
                  <h1 className="text-4xl font-black uppercase text-zinc-100 mb-4">404</h1>
                  <p className="text-zinc-400 mb-6 uppercase tracking-widest">Page not found</p>
                  <button
                    onClick={() => window.history.back()}
                    className="btn btn-primary"
                  >
                    Go Back
                  </button>
                </div>
              </div>
            }
          />
        </Routes>
      </Suspense>
    </div>
  );
}

export default App;






