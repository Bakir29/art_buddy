import axios, { AxiosInstance } from 'axios';
import { 
  ApiResponse, 
  PaginatedResponse,
  LoginCredentials, 
  RegisterData, 
  AuthTokens,
  User,
  Lesson,
  Quiz,
  Progress,
  ProgressSummary,
  Reminder,
  ChatMessage,
  TutorResponse,
  Notification,
  Recommendation
} from '@/types';

// Create axios instance with base configuration
const createApiClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request interceptor to add auth token
  client.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Response interceptor for error handling
  client.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }
  );

  return client;
};

export const apiClient = createApiClient();

// Authentication API
export const authApi = {
  login: async (credentials: LoginCredentials): Promise<AuthTokens> => {
    const params = new URLSearchParams();
    params.append('username', credentials.email);
    params.append('password', credentials.password);
    
    const response = await apiClient.post('/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  register: async (data: RegisterData): Promise<ApiResponse<User>> => {
    const response = await apiClient.post('/auth/register', data);
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },

  logout: async (): Promise<void> => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
  },
};

// Dashboard API (Optimized single endpoint)
export const dashboardApi = {
  getDashboardData: async (): Promise<ApiResponse<{
    progress: ProgressSummary;
    recent_lessons: Lesson[];
    stats: any;
    user_info: {
      name: string;
      email: string;
      id: string;
    };
  }>> => {
    const response = await apiClient.get('/api/dashboard');
    return response.data;
  },
};

// Users API
export const usersApi = {
  getProfile: async (): Promise<ApiResponse<User>> => {
    const response = await apiClient.get('/users/profile');
    return response.data;
  },

  updateProfile: async (data: Partial<User>): Promise<ApiResponse<User>> => {
    const response = await apiClient.put('/users/profile', data);
    return response.data;
  },

  getStats: async (): Promise<ApiResponse<ProgressSummary>> => {
    const response = await apiClient.get('/users/stats');
    return response.data;
  },
};

// Lessons API
export const lessonsApi = {
  getAll: async (params?: { 
    difficulty?: string; 
    lesson_type?: string; 
    page?: number; 
    limit?: number;
  }): Promise<Lesson[]> => {
    const response = await apiClient.get('/lessons', { params });
    return response.data;
  },

  getById: async (id: string): Promise<ApiResponse<Lesson>> => {
    const response = await apiClient.get(`/lessons/${id}`);
    // Backend returns Lesson directly, wrap it in ApiResponse format
    return { success: true, data: response.data };
  },

  searchLessons: async (query: string): Promise<ApiResponse<Lesson[]>> => {
    const response = await apiClient.get('/lessons/search', { 
      params: { query }
    });
    return response.data;
  },
};

// AI API (RAG and Chat)
export const aiApi = {
  askQuestion: async (data: {
    user_id: string;
    question: string;
    context?: string;
  }): Promise<{
    answer: string;
    sources?: Array<{ source: string; content: string }>;
    model_used?: string;
    confidence_score?: number;
  }> => {
    const response = await apiClient.post('/ai/ask', data);
    return response.data;
  },

  getKnowledgeStats: async (): Promise<{
    total_knowledge_chunks: number;
    knowledge_sources: number;
    available_sources: string[];
  }> => {
    const response = await apiClient.get('/ai/knowledge-stats');
    return response.data;
  },

  ingestText: async (data: {
    content: string;
    source: string;
  }): Promise<ApiResponse<{
    message: string;
    chunks_created: number;
    source: string;
  }>> => {
    const formData = new FormData();
    formData.append('content', data.content);
    formData.append('source', data.source);
    
    const response = await apiClient.post('/ai/ingest-text', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  analyzeImage: async (file: File, prompt?: string): Promise<ApiResponse<{
    analysis: string;
    suggestions: string[];
    techniques_used: string[];
    skill_level_assessment: string;
  }>> => {
    const formData = new FormData();
    formData.append('file', file);
    if (prompt) {
      formData.append('prompt', prompt);
    }
    
    const response = await apiClient.post('/ai/analyze-image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

// MCP API (Model Context Protocol)
export const mcpApi = {
  getAvailableTools: async (): Promise<ApiResponse<Array<{
    name: string;
    description: string;
    parameters: Record<string, any>;
  }>>> => {
    const response = await apiClient.get('/mcp/tools');
    return response.data;
  },

  executeTool: async (toolName: string, parameters: Record<string, any>): Promise<ApiResponse<any>> => {
    const response = await apiClient.post('/mcp/execute', {
      tool_name: toolName,
      parameters
    });
    return response.data;
  },

  getUserProgress: async (): Promise<ApiResponse<any>> => {
    const response = await apiClient.post('/mcp/tools/get_user_progress', {});
    return response.data;
  },

  updateProgress: async (data: {
    lesson_id: string;
    completion_status: string;
    score_percentage?: number;
  }): Promise<ApiResponse<any>> => {
    const response = await apiClient.post('/mcp/tools/update_progress', data);
    return response.data;
  },

  generateLesson: async (data: {
    topic: string;
    difficulty_level: string;
    duration_minutes: number;
  }): Promise<ApiResponse<any>> => {
    const response = await apiClient.post('/mcp/tools/generate_lesson', data);
    return response.data;
  },

  scheduleReminder: async (data: {
    reminder_type: string;
    message: string;
    scheduled_for: string;
  }): Promise<ApiResponse<any>> => {
    const response = await apiClient.post('/mcp/tools/schedule_reminder', data);
    return response.data;
  },
};

// Workflows API (n8n Integration)
export const workflowsApi = {
  triggerWorkflow: async (workflowType: string, data: Record<string, any>): Promise<ApiResponse<{
    workflow_id: string;
    status: string;
    message: string;
  }>> => {
    const response = await apiClient.post('/workflows/trigger', {
      workflow_type: workflowType,
      data
    });
    return response.data;
  },

  getWorkflowStatus: async (workflowId: string): Promise<ApiResponse<{
    id: string;
    status: string;
    created_at: string;
    completed_at?: string;
    result?: any;
  }>> => {
    const response = await apiClient.get(`/workflows/${workflowId}/status`);
    return response.data;
  },

  getStatus: async (): Promise<ApiResponse<any>> => {
    const response = await apiClient.get('/api/v1/workflows/status');
    return response.data;
  },

  getAnalytics: async (days = 7): Promise<ApiResponse<any>> => {
    const response = await apiClient.get('/api/v1/workflows/analytics', {
      params: { days }
    });
    return response.data;
  },

  simulateLessonCompletion: async (data: {
    lesson_id: string;
    score?: number;
    time_spent_minutes?: number;
  }): Promise<ApiResponse<any>> => {
    const response = await apiClient.post('/api/v1/workflows/simulate/lesson-completion', data);
    return response.data;
  },

  simulateQuizCompletion: async (data: {
    quiz_id: string;
    score?: number;
    total_questions?: number;
    correct_answers?: number;
  }): Promise<ApiResponse<any>> => {
    const response = await apiClient.post('/api/v1/workflows/simulate/quiz-completion', data);
    return response.data;
  },

  simulateDailyReminder: async (): Promise<ApiResponse<any>> => {
    const response = await apiClient.post('/api/v1/workflows/simulate/daily-reminder');
    return response.data;
  },
};

// Quiz API
export const quizApi = {
  getByLessonId: async (lessonId: string): Promise<ApiResponse<Quiz>> => {
    const response = await apiClient.get(`/lessons/${lessonId}/quiz`);
    return response.data;
  },

  submitAnswers: async (
    quizId: string, 
    answers: Record<string, any>
  ): Promise<ApiResponse<{
    score_percentage: number;
    correct_answers: number;
    total_questions: number;
    passed: boolean;
    feedback: string;
  }>> => {
    const response = await apiClient.post(`/quiz/${quizId}/submit`, { answers });
    return response.data;
  },
};

// Progress API
export const progressApi = {
  getUserProgress: async (userId?: string, params?: {
    lesson_id?: string;
    status?: string;
    page?: number;
    limit?: number;
    user_id?: string;
  }): Promise<Progress[]> => {
    const response = await apiClient.get('/progress/me');
    return response.data;
  },

  getSummary: async (): Promise<ApiResponse<ProgressSummary>> => {
    const response = await apiClient.get('/progress/summary');
    return response.data;
  },

  startLesson: async (lessonId: string): Promise<any> => {
    const response = await apiClient.post(`/progress/start-lesson?lesson_id=${lessonId}`);
    return response.data;
  },

  updateProgress: async (
    lessonId: string,
    data: { 
      completion_status: string;
      score?: number;
      time_spent_minutes?: number;
    }
  ): Promise<any> => {
    // Use complete-lesson endpoint for completing, or start-lesson for starting
    if (data.completion_status === 'completed') {
      const params = new URLSearchParams({ lesson_id: lessonId });
      if (data.score !== undefined) params.set('score', String(data.score));
      const response = await apiClient.post(`/progress/complete-lesson?${params.toString()}`);
      return response.data;
    } else if (data.completion_status === 'in_progress') {
      const response = await apiClient.post(`/progress/start-lesson?lesson_id=${lessonId}`);
      return response.data;
    }
    return null;
  },

  completeLesson: async (
    lessonId: string, 
    data: { time_spent_minutes: number; score_percentage?: number }
  ): Promise<ApiResponse<Progress>> => {
    const response = await apiClient.post('/progress/complete', {
      lesson_id: lessonId,
      ...data
    });
    return response.data;
  },
};

// Recommendations API
export const recommendationsApi = {
  getPersonalized: async (): Promise<ApiResponse<Recommendation[]>> => {
    const response = await apiClient.get('/recommendations');
    return response.data;
  },

  getNextLesson: async (): Promise<ApiResponse<Lesson | null>> => {
    const response = await apiClient.get('/recommendations/next-lesson');
    return response.data;
  },
};

// Reminders API
export const remindersApi = {
  getAll: async (): Promise<ApiResponse<Reminder[]>> => {
    const response = await apiClient.get('/reminders');
    return response.data;
  },

  create: async (data: Omit<Reminder, 'id' | 'user_id' | 'created_at' | 'is_sent'>): Promise<ApiResponse<Reminder>> => {
    const response = await apiClient.post('/reminders', data);
    return response.data;
  },

  update: async (id: string, data: Partial<Reminder>): Promise<ApiResponse<Reminder>> => {
    const response = await apiClient.put(`/reminders/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<ApiResponse<void>> => {
    const response = await apiClient.delete(`/reminders/${id}`);
    return response.data;
  },
};

// AI Tutor API
export const tutorApi = {
  chat: async (
    message: string, 
    context?: { lesson_id?: string; topic?: string }
  ): Promise<ApiResponse<TutorResponse>> => {
    const response = await apiClient.post('/ai/chat', {
      message,
      context
    });
    return response.data;
  },

  getChatHistory: async (limit = 50): Promise<ApiResponse<ChatMessage[]>> => {
    const response = await apiClient.get('/ai/chat/history', {
      params: { limit }
    });
    return response.data;
  },

  getExplanation: async (
    concept: string,
    context?: { lesson_id?: string }
  ): Promise<ApiResponse<{ explanation: string; examples: string[]; resources: any[] }>> => {
    const response = await apiClient.post('/ai/explain', {
      concept,
      context
    });
    return response.data;
  },
};

// Notifications API (placeholder for future implementation)
export const notificationsApi = {
  getAll: async (): Promise<ApiResponse<Notification[]>> => {
    // This would integrate with a notification service
    return { success: true, data: [] };
  },

  markAsRead: async (notificationId: number): Promise<ApiResponse<void>> => {
    // Placeholder for marking notifications as read
    // TODO: Implement actual API call using notificationId
    console.log('Marking notification as read:', notificationId);
    return { success: true };
  },
};

// Export all APIs
export const api = {
  auth: authApi,
  users: usersApi,
  lessons: lessonsApi,
  quiz: quizApi,
  progress: progressApi,
  recommendations: recommendationsApi,
  reminders: remindersApi,
  tutor: tutorApi,
  mcp: mcpApi,
  workflows: workflowsApi,
  notifications: notificationsApi,
};