// Core entity types matching backend models
export interface User {
  id: string;
  email: string;
  name: string;
  skill_level: 'beginner' | 'intermediate' | 'advanced';
  created_at: string;
  updated_at: string;
  art_interests?: string[];
  learning_goals?: string[];
  notification_preferences?: {
    daily_reminders: boolean;
    progress_updates: boolean;
    new_lessons: boolean;
    achievement_notifications: boolean;
  };
  bio?: string;
  profile_picture?: string;
}

export interface Lesson {
  id: string;
  title: string;
  description?: string;
  content: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  category: string;
  order_in_category: number;
  lesson_type: string;
  duration_minutes: number;
  prerequisites: string[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface LessonResource {
  type: 'video' | 'image' | 'document' | 'link';
  title: string;
  url: string;
  description?: string;
}

export interface Quiz {
  id: string;
  lesson_id: string;
  title: string;
  description: string;
  questions: QuizQuestion[];
  time_limit_minutes?: number;
  passing_score: number;
}

export interface QuizQuestion {
  id: string;
  question: string;
  type: 'multiple_choice' | 'true_false' | 'short_answer';
  options?: string[];
  correct_answer: string | string[];
  explanation?: string;
  points: number;
}

export interface Progress {
  id: string;
  user_id: string;
  lesson_id: string;
  completion_status: 'not_started' | 'in_progress' | 'completed';
  score_percentage?: number;
  time_spent_minutes: number;
  started_at?: string;
  completed_at?: string;
  lesson?: Lesson;
}

export interface Reminder {
  id: string;
  user_id: string;
  title: string;
  message: string;
  reminder_type: 'practice' | 'lesson' | 'quiz' | 'review' | 'general';
  scheduled_for: string;
  is_sent: boolean;
  created_at: string;
}

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    total_pages: number;
  };
}

// Authentication types
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  name: string;
  skill_level: 'beginner' | 'intermediate' | 'advanced';
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
  expires_in: number;
}

// Dashboard and analytics types
export interface ProgressSummary {
  total_lessons: number;
  completed_lessons: number;
  in_progress_lessons: number;
  average_score: number;
  total_time_spent: number;
  current_streak: number;
  longest_streak: number;
  skill_level: string;
  recent_activity: RecentActivity[];
  skill_progress?: Record<string, number>;
  lessons_this_week?: number;
}

export interface RecentActivity {
  id: string;
  type: 'lesson_completed' | 'quiz_taken' | 'milestone_reached';
  title: string;
  description: string;
  timestamp: string;
  score?: number;
}

// AI Tutor types
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  metadata?: {
    lesson_id?: string;
    tools_used?: string[];
    sources?: string[];
  };
}

export interface TutorResponse {
  message: string;
  suggestions?: string[];
  related_lessons?: Lesson[];
  next_steps?: string[];
}

// Workflow and notification types
export interface WorkflowEvent {
  event_id: string;
  event_type: string;
  user_id: string;
  timestamp: string;
  data: Record<string, any>;
}

export interface Notification {
  id: string;
  user_id: string;
  type: string;
  title: string;
  message: string;
  priority: 'low' | 'normal' | 'high';
  is_read: boolean;
  created_at: string;
  metadata?: Record<string, any>;
}

// Gamification types
export interface Achievement {
  id: string;
  title: string;
  description: string;
  badge_url?: string;
  earned_at: string;
  category: string;
}

export interface Reward {
  id: string;
  type: 'points' | 'badge' | 'unlock';
  points?: number;
  title: string;
  description: string;
  granted_at: string;
}

// Search and recommendation types
export interface SearchResult {
  id: string;
  type: 'lesson' | 'resource' | 'concept';
  title: string;
  description: string;
  relevance_score: number;
  url?: string;
}

export interface Recommendation {
  id: string;
  type: 'lesson' | 'practice' | 'review';
  title: string;
  description: string;
  reason: string;
  confidence_score: number;
  estimated_time: number;
  item?: Lesson | Quiz;
}

// Form validation types
export interface FormErrors {
  [key: string]: string | undefined;
}

export interface ValidationResult {
  isValid: boolean;
  errors: FormErrors;
}

// Component prop types
export interface BaseComponentProps {
  className?: string;
  children?: React.ReactNode;
}

export interface LoadingState {
  isLoading: boolean;
  error?: string;
}

// Chart and visualization types
export interface ChartDataPoint {
  label: string;
  value: number;
  date?: string;
}

export interface ProgressChart {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    borderColor: string;
    backgroundColor: string;
  }[];
}