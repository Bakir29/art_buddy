import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User, LoginCredentials, RegisterData } from '@/types';
import { api } from '@/services/api';
import toast from 'react-hot-toast';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

interface AuthActions {
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  getCurrentUser: () => Promise<void>;
  updateProfile: (data: Partial<User>) => Promise<void>;
  clearError: () => void;
  setLoading: (loading: boolean) => void;
}

type AuthStore = AuthState & AuthActions;

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Actions
      login: async (credentials: LoginCredentials) => {
        set({ isLoading: true, error: null });
        
        try {
          const tokens = await api.auth.login(credentials);
          const token = tokens.access_token;
          
          // Store token
          localStorage.setItem('auth_token', token);
          
          // Get user profile
          const user = await api.auth.getCurrentUser();
          
          set({ 
            user, 
            token, 
            isAuthenticated: true, 
            isLoading: false,
            error: null 
          });
          
          toast.success(`Welcome back, ${user.name}!`);
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || 'Login failed';
          set({ 
            error: errorMessage, 
            isLoading: false,
            isAuthenticated: false,
            user: null,
            token: null
          });
          toast.error(errorMessage);
          throw error;
        }
      },

      register: async (data: RegisterData) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await api.auth.register(data);
          
          if (response.success && response.data) {
            // Auto-login after successful registration
            await get().login({
              email: data.email,
              password: data.password
            });
            
            toast.success('Account created successfully!');
          } else {
            throw new Error(response.error || 'Registration failed');
          }
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || error.message || 'Registration failed';
          set({ 
            error: errorMessage, 
            isLoading: false 
          });
          toast.error(errorMessage);
          throw error;
        }
      },

      logout: async () => {
        set({ isLoading: true });
        
        try {
          await api.auth.logout();
          
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            error: null
          });
          
          // Clear localStorage
          localStorage.removeItem('auth_token');
          localStorage.removeItem('user');
          
          toast.success('Logged out successfully');
        } catch (error) {
          // Even if the API call fails, we should still log out locally
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            error: null
          });
          
          localStorage.removeItem('auth_token');
          localStorage.removeItem('user');
        }
      },

      getCurrentUser: async () => {
        const token = localStorage.getItem('auth_token');
        if (!token) return;
        
        set({ isLoading: true, error: null });
        
        try {
          const user = await api.auth.getCurrentUser();
          set({ 
            user, 
            token, 
            isAuthenticated: true, 
            isLoading: false,
            error: null 
          });
        } catch (error: any) {
          // Token is invalid
          localStorage.removeItem('auth_token');
          localStorage.removeItem('user');
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            error: null
          });
        }
      },

      updateProfile: async (data: Partial<User>) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await api.users.updateProfile(data);
          
          if (response.success && response.data) {
            set({ 
              user: response.data, 
              isLoading: false,
              error: null 
            });
            toast.success('Profile updated successfully!');
          } else {
            throw new Error(response.error || 'Update failed');
          }
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || error.message || 'Update failed';
          set({ 
            error: errorMessage, 
            isLoading: false 
          });
          toast.error(errorMessage);
          throw error;
        }
      },

      clearError: () => set({ error: null }),
      
      setLoading: (loading: boolean) => set({ isLoading: loading }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);