import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/useAuthStore';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { toast } from 'react-hot-toast';

export function RegisterPage() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  
  const { register } = useAuthStore();
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (formData.password !== formData.confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    setIsLoading(true);

    try {
      await register({
        email: formData.email,
        password: formData.password,
        name: formData.username, // Using username as name
        skill_level: 'beginner'
      });
      toast.success('Account created successfully!');
      navigate('/dashboard');
    } catch (error: any) {
      toast.error(error.message || 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <div className="text-center mb-8">
        <h2 className="text-2xl font-black tracking-tight text-white uppercase">Create Account</h2>
        <p className="mt-2 text-sm text-zinc-500">
          Already have an account?{' '}
          <Link to="/login" className="font-semibold text-orange-500 hover:text-orange-400">
            Sign in
          </Link>
        </p>
      </div>

      <form className="space-y-5" onSubmit={handleSubmit}>
        {[
          { id: 'username', label: 'Username', type: 'text', placeholder: 'Choose a username', autoComplete: 'username' },
          { id: 'email', label: 'Email Address', type: 'email', placeholder: 'Enter your email', autoComplete: 'email' },
          { id: 'password', label: 'Password', type: 'password', placeholder: 'Create a password', autoComplete: 'new-password' },
          { id: 'confirmPassword', label: 'Confirm Password', type: 'password', placeholder: 'Confirm your password', autoComplete: 'new-password' },
        ].map(field => (
          <div key={field.id}>
            <label htmlFor={field.id} className="block text-xs font-semibold text-zinc-400 uppercase tracking-widest">
              {field.label}
            </label>
            <div className="mt-1">
              <input
                id={field.id}
                name={field.id}
                type={field.type}
                required
                autoComplete={(field as any).autoComplete}
                value={(formData as any)[field.id]}
                onChange={handleChange}
                className="appearance-none block w-full px-3 py-2.5 border border-zinc-700 bg-zinc-800 text-white placeholder-zinc-600 focus:outline-none focus:ring-1 focus:ring-orange-500 focus:border-orange-500 text-sm"
                placeholder={field.placeholder}
              />
            </div>
          </div>
        ))}

        <div className="flex items-center">
          <input
            id="terms"
            name="terms"
            type="checkbox"
            required
            className="h-4 w-4 text-orange-500 focus:ring-orange-500 border-zinc-700 bg-zinc-800"
          />
          <label htmlFor="terms" className="ml-2 block text-sm text-zinc-400">
            I agree to the{' '}
            <a href="#" className="text-orange-500 hover:text-orange-400">
              Terms and Conditions
            </a>
          </label>
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
              'Create Account'
            )}
          </button>
        </div>
      </form>
    </div>
  );
}







