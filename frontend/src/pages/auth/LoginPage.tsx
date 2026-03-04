import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/useAuthStore';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { toast } from 'react-hot-toast';
import { usePrefetchDashboard } from '@/hooks/usePrefetchDashboard';

export function LoginPage() {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  
  const { login } = useAuthStore();
  const navigate = useNavigate();
  const { prefetchDashboard } = usePrefetchDashboard();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await login({ 
        email: formData.username, // Using username field as email
        password: formData.password 
      });
      
      // Prefetch dashboard data immediately after successful login
      prefetchDashboard();
      
      toast.success('Welcome back!');
      navigate('/dashboard');
    } catch (error: any) {
      toast.error(error.message || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <div className="text-center mb-8">
        <h2 className="text-2xl font-black tracking-tight text-white uppercase">Sign In</h2>
        <p className="mt-2 text-sm text-zinc-500">
          Don't have an account?{' '}
          <Link to="/register" className="font-semibold text-orange-500 hover:text-orange-400">
            Sign up
          </Link>
        </p>
      </div>

      <form className="space-y-6" onSubmit={handleSubmit}>
        <div>
          <label htmlFor="username" className="block text-xs font-semibold text-zinc-400 uppercase tracking-widest">
            Email
          </label>
          <div className="mt-1">
            <input
              id="username"
              name="username"
              type="email"
              required
              autoComplete="email"
              value={formData.username}
              onChange={handleChange}
              className="appearance-none block w-full px-3 py-2.5 border border-zinc-700 bg-zinc-800 text-white placeholder-zinc-600 focus:outline-none focus:ring-1 focus:ring-orange-500 focus:border-orange-500 text-sm"
              placeholder="Enter your email"
            />
          </div>
        </div>

        <div>
          <label htmlFor="password" className="block text-xs font-semibold text-zinc-400 uppercase tracking-widest">
            Password
          </label>
          <div className="mt-1">
            <input
              id="password"
              name="password"
              type="password"
              required
              autoComplete="current-password"
              value={formData.password}
              onChange={handleChange}
              className="appearance-none block w-full px-3 py-2.5 border border-zinc-700 bg-zinc-800 text-white placeholder-zinc-600 focus:outline-none focus:ring-1 focus:ring-orange-500 focus:border-orange-500 text-sm"
              placeholder="Enter your password"
            />
          </div>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <input
              id="remember-me"
              name="remember-me"
              type="checkbox"
              className="h-4 w-4 text-orange-500 focus:ring-orange-500 border-zinc-700 bg-zinc-800"
            />
            <label htmlFor="remember-me" className="ml-2 block text-sm text-zinc-400">
              Remember me
            </label>
          </div>

          <div className="text-sm">
            <a href="#" className="font-medium text-orange-500 hover:text-orange-400">
              Forgot your password?
            </a>
          </div>
        </div>

        <div>
          <button
            type="submit"
            disabled={isLoading}
            className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-bold uppercase tracking-widest text-white bg-orange-500 hover:bg-orange-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-zinc-900 focus:ring-orange-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <LoadingSpinner size="sm" className="text-white" />
            ) : (
              'Sign in'
            )}
          </button>
        </div>
      </form>
    </div>
  );
}







