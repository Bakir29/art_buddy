import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { formatDistanceToNow, format, parseISO } from 'date-fns';

// Utility for merging Tailwind CSS classes
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Date formatting utilities
export const formatDate = {
  // Format date for display (e.g., "Jan 15, 2024")
  display: (date: string | Date): string => {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return format(dateObj, 'MMM d, yyyy');
  },

  // Format date with time (e.g., "Jan 15, 2024 at 3:30 PM")
  displayWithTime: (date: string | Date): string => {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return format(dateObj, 'MMM d, yyyy \'at\' h:mm a');
  },

  // Relative time (e.g., "2 hours ago")
  relative: (date: string | Date): string => {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return formatDistanceToNow(dateObj, { addSuffix: true });
  },

  // Format for input fields (YYYY-MM-DD)
  input: (date: string | Date): string => {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return format(dateObj, 'yyyy-MM-dd');
  },

  // Format duration in minutes to human readable
  duration: (minutes: number): string => {
    if (minutes < 60) {
      return `${minutes} min`;
    }
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    if (remainingMinutes === 0) {
      return `${hours}h`;
    }
    return `${hours}h ${remainingMinutes}m`;
  },
};

// Number formatting utilities
export const formatNumber = {
  // Format percentage (e.g., 85.5 -> "86%")
  percentage: (value: number): string => {
    return `${Math.round(value)}%`;
  },

  // Format score with color coding
  score: (value: number): { text: string; color: string } => {
    const percentage = Math.round(value);
    let color = 'text-gray-600';
    
    if (percentage >= 90) color = 'text-green-600';
    else if (percentage >= 80) color = 'text-blue-600';
    else if (percentage >= 70) color = 'text-yellow-600';
    else if (percentage >= 60) color = 'text-orange-600';
    else color = 'text-red-600';
    
    return { text: `${percentage}%`, color };
  },

  // Format large numbers (e.g., 1234 -> "1.2K")
  compact: (value: number): string => {
    if (value < 1000) return value.toString();
    if (value < 1000000) return `${(value / 1000).toFixed(1)}K`;
    return `${(value / 1000000).toFixed(1)}M`;
  },
};

// Text utilities
export const formatText = {
  // Capitalize first letter
  capitalize: (text: string): string => {
    return text.charAt(0).toUpperCase() + text.slice(1);
  },

  // Convert snake_case to Title Case
  titleCase: (text: string): string => {
    return text
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  },

  // Truncate text with ellipsis
  truncate: (text: string, maxLength: number): string => {
    if (text.length <= maxLength) return text;
    return `${text.slice(0, maxLength - 3)}...`;
  },

  // Extract initials from name
  initials: (name: string): string => {
    return name
      .split(' ')
      .map(word => word.charAt(0).toUpperCase())
      .slice(0, 2)
      .join('');
  },
};

// Validation utilities
export const validation = {
  // Email validation
  isEmail: (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  },

  // Password strength validation
  isStrongPassword: (password: string): { 
    isValid: boolean; 
    errors: string[] 
  } => {
    const errors: string[] = [];
    
    if (password.length < 8) {
      errors.push('Password must be at least 8 characters long');
    }
    if (!/[A-Z]/.test(password)) {
      errors.push('Password must contain at least one uppercase letter');
    }
    if (!/[a-z]/.test(password)) {
      errors.push('Password must contain at least one lowercase letter');
    }
    if (!/\d/.test(password)) {
      errors.push('Password must contain at least one number');
    }
    
    return {
      isValid: errors.length === 0,
      errors,
    };
  },

  // Name validation
  isValidName: (name: string): boolean => {
    return name.trim().length >= 2 && /^[a-zA-Z\s]+$/.test(name.trim());
  },
};

// Color utilities for skill levels and statuses
export const getSkillLevelColor = (level: string): string => {
  switch (level) {
    case 'beginner':
      return 'bg-green-100 text-green-800';
    case 'intermediate':
      return 'bg-blue-100 text-blue-800';
    case 'advanced':
      return 'bg-purple-100 text-purple-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

export const getStatusColor = (status: string): string => {
  switch (status) {
    case 'completed':
      return 'bg-green-100 text-green-800';
    case 'in_progress':
      return 'bg-blue-100 text-blue-800';
    case 'not_started':
      return 'bg-gray-100 text-gray-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

export const getPriorityColor = (priority: string): string => {
  switch (priority) {
    case 'high':
      return 'bg-red-100 text-red-800';
    case 'medium':
    case 'normal':
      return 'bg-yellow-100 text-yellow-800';
    case 'low':
      return 'bg-gray-100 text-gray-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

// Local storage utilities
export const storage = {
  set: <T>(key: string, value: T): void => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error('Failed to save to localStorage:', error);
    }
  },

  get: <T>(key: string): T | null => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : null;
    } catch (error) {
      console.error('Failed to read from localStorage:', error);
      return null;
    }
  },

  remove: (key: string): void => {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.error('Failed to remove from localStorage:', error);
    }
  },

  clear: (): void => {
    try {
      localStorage.clear();
    } catch (error) {
      console.error('Failed to clear localStorage:', error);
    }
  },
};

// Debounce utility for search and form inputs
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}