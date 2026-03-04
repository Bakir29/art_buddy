import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { authApi } from '@/services/api';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { toast } from 'react-hot-toast';

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const [formData, setFormData] = useState({
    token: searchParams.get('token') || '',
    new_password: '',
    confirm_password: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (formData.new_password !== formData.confirm_password) {
      toast.error('Passwords do not match');
      return;
    }

    setIsLoading(true);
    try {
      await authApi.resetPassword(formData.token, formData.new_password);
      toast.success('Password reset successfully! Please sign in.');
      navigate('/login');
    } catch (error: any) {
      const message =
        error.response?.data?.detail || error.message || 'Failed to reset password';
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <div className="text-center mb-8">
        <h2 className="text-2xl font-black tracking-tight text-white uppercase">New Password</h2>
        <p className="mt-2 text-sm text-zinc-500">Enter your reset token and choose a new password.</p>
      </div>

      <form className="space-y-6" onSubmit={handleSubmit}>
        <div>
          <label
            htmlFor="token"
            className="block text-xs font-semibold text-zinc-400 uppercase tracking-widest"
          >
            Reset Token
          </label>
          <div className="mt-1">
            <input
              id="token"
              name="token"
              type="text"
              required
              value={formData.token}
              onChange={handleChange}
              className="appearance-none block w-full px-3 py-2.5 border border-zinc-700 bg-zinc-800 text-white placeholder-zinc-600 focus:outline-none focus:ring-1 focus:ring-orange-500 focus:border-orange-500 text-sm font-mono"
              placeholder="Paste your reset token"
            />
          </div>
        </div>

        <div>
          <label
            htmlFor="new_password"
            className="block text-xs font-semibold text-zinc-400 uppercase tracking-widest"
          >
            New Password
          </label>
          <div className="mt-1">
            <input
              id="new_password"
              name="new_password"
              type="password"
              required
              autoComplete="new-password"
              minLength={8}
              value={formData.new_password}
              onChange={handleChange}
              className="appearance-none block w-full px-3 py-2.5 border border-zinc-700 bg-zinc-800 text-white placeholder-zinc-600 focus:outline-none focus:ring-1 focus:ring-orange-500 focus:border-orange-500 text-sm"
              placeholder="Minimum 8 characters"
            />
          </div>
        </div>

        <div>
          <label
            htmlFor="confirm_password"
            className="block text-xs font-semibold text-zinc-400 uppercase tracking-widest"
          >
            Confirm Password
          </label>
          <div className="mt-1">
            <input
              id="confirm_password"
              name="confirm_password"
              type="password"
              required
              autoComplete="new-password"
              value={formData.confirm_password}
              onChange={handleChange}
              className="appearance-none block w-full px-3 py-2.5 border border-zinc-700 bg-zinc-800 text-white placeholder-zinc-600 focus:outline-none focus:ring-1 focus:ring-orange-500 focus:border-orange-500 text-sm"
              placeholder="Repeat new password"
            />
          </div>
        </div>

        <div>
          <button
            type="submit"
            disabled={isLoading}
            className="w-full flex justify-center py-2.5 px-4 border border-transparent text-sm font-bold text-white uppercase tracking-widest bg-orange-600 hover:bg-orange-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
          >
            {isLoading ? <LoadingSpinner size="sm" /> : 'Reset Password'}
          </button>
        </div>
      </form>

      <p className="mt-6 text-center text-sm text-zinc-500">
        Back to{' '}
        <Link to="/login" className="font-semibold text-orange-500 hover:text-orange-400">
          Sign in
        </Link>
      </p>
    </div>
  );
}
