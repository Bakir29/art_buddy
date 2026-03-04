import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authApi } from '@/services/api';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { toast } from 'react-hot-toast';

export function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const data = await authApi.forgotPassword(email);
      toast.success('Reset token generated!');
      navigate(`/reset-password?token=${encodeURIComponent(data.reset_token)}`);
    } catch (error: any) {
      const message =
        error.response?.data?.detail || error.message || 'No account found with that email';
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <div className="text-center mb-8">
        <h2 className="text-2xl font-black tracking-tight text-white uppercase">Reset Password</h2>
        <p className="mt-2 text-sm text-zinc-500">
          Enter your email and we'll generate a reset token.
        </p>
      </div>

      <form className="space-y-6" onSubmit={handleSubmit}>
        <div>
          <label
            htmlFor="email"
            className="block text-xs font-semibold text-zinc-400 uppercase tracking-widest"
          >
            Email
          </label>
          <div className="mt-1">
            <input
              id="email"
              name="email"
              type="email"
              required
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="appearance-none block w-full px-3 py-2.5 border border-zinc-700 bg-zinc-800 text-white placeholder-zinc-600 focus:outline-none focus:ring-1 focus:ring-orange-500 focus:border-orange-500 text-sm"
              placeholder="Enter your account email"
            />
          </div>
        </div>

        <div>
          <button
            type="submit"
            disabled={isLoading}
            className="w-full flex justify-center py-2.5 px-4 border border-transparent text-sm font-bold text-white uppercase tracking-widest bg-orange-600 hover:bg-orange-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
          >
            {isLoading ? <LoadingSpinner size="sm" /> : 'Get Reset Token'}
          </button>
        </div>
      </form>

      <p className="mt-6 text-center text-sm text-zinc-500">
        Remembered your password?{' '}
        <Link to="/login" className="font-semibold text-orange-500 hover:text-orange-400">
          Sign in
        </Link>
      </p>
    </div>
  );
}
