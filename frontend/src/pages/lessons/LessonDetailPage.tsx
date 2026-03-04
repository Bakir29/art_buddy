import { useState, useMemo } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { lessonsApi, progressApi } from '@/services/api';
import { useAuthStore } from '@/stores/useAuthStore';
import {
  CheckCircleIcon,
  ClockIcon,
  ArrowLeftIcon,
  LightBulbIcon,
  AcademicCapIcon,
  SparklesIcon
} from '@heroicons/react/24/outline';

interface Lesson {
  id: string;
  title: string;
  content: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  category: string;
  lesson_type: string;
  duration_minutes: number;
  prerequisites: string[];
}

interface ContentCard {
  type: 'heading' | 'paragraph' | 'list' | 'tip';
  content: string;
  items?: string[];
}

export function LessonDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  useAuthStore();
  const queryClient = useQueryClient();
  
  const [isCompleting, setIsCompleting] = useState(false);

  // Fetch lesson details
  const { data: lessonResponse, isLoading, error, isError } = useQuery({
    queryKey: ['lessons', 'detail', id],
    queryFn: () => lessonsApi.getById(id!),
    enabled: !!id,
    staleTime: 1000 * 60 * 10, // 10 minutes - lesson content rarely changes
    gcTime: 1000 * 60 * 15, // 15 minutes
    retry: 2,
  });

  const lesson = lessonResponse?.data as Lesson;

  // Parse markdown content into cards
  const contentCards = useMemo(() => {
    if (!lesson?.content) return [];
    
    const cards: ContentCard[] = [];
    const lines = lesson.content.split('\n').filter(line => line.trim());
    
    let currentList: string[] = [];
    
    for (const line of lines) {
      // Heading
      if (line.startsWith('# ')) {
        if (currentList.length > 0) {
          cards.push({ type: 'list', content: '', items: currentList });
          currentList = [];
        }
        cards.push({ type: 'heading', content: line.replace(/^#+ /, '') });
      }
      // Subheading
      else if (line.startsWith('## ')) {
        if (currentList.length > 0) {
          cards.push({ type: 'list', content: '', items: currentList });
          currentList = [];
        }
        cards.push({ type: 'heading', content: line.replace(/^##+ /, '') });
      }
      // List item
      else if (line.startsWith('- ')) {
        currentList.push(line.replace(/^- /, ''));
      }
      // Paragraph
      else if (line.trim()) {
        if (currentList.length > 0) {
          cards.push({ type: 'list', content: '', items: currentList });
          currentList = [];
        }
        cards.push({ type: 'paragraph', content: line });
      }
    }
    
    // Add remaining list
    if (currentList.length > 0) {
      cards.push({ type: 'list', content: '', items: currentList });
    }
    
    return cards;
  }, [lesson?.content]);

  // Mark lesson as completed
  const completeLessonMutation = useMutation({
    mutationFn: async () => {
      setIsCompleting(true);
      return await progressApi.updateProgress(String(id!), {
        completion_status: 'completed',
        score: 100
      });
    },
    onSuccess: () => {
      // Only invalidate progress data - lesson content itself doesn't change on completion.
      // Avoid invalidating ['lessons', 'detail', id] which would cause the current page to go blank.
      queryClient.invalidateQueries({ queryKey: ['progress'] });
      setIsCompleting(false);
    },
    onError: () => {
      setIsCompleting(false);
    }
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-zinc-950 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-orange-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-zinc-500">Loading lesson...</p>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="min-h-screen bg-zinc-950 flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="bg-zinc-900 border border-red-900/50 p-6 mb-4">
            <p className="text-red-400 font-semibold mb-2">Failed to load lesson</p>
            <p className="text-red-500/70 text-sm mb-4">
              {error instanceof Error ? error.message : 'An error occurred while loading the lesson'}
            </p>
            <p className="text-zinc-500 text-sm">Lesson ID: {id}</p>
          </div>
          <button
            onClick={() => navigate('/lessons')}
            className="px-4 py-2 bg-orange-500 text-white font-bold uppercase tracking-widest hover:bg-orange-600"
          >
            Back to Lessons
          </button>
        </div>
      </div>
    );
  }

  if (!lesson) {
    return (
      <div className="min-h-screen bg-zinc-950 flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="bg-zinc-900 border border-yellow-900/50 p-6 mb-4">
            <p className="text-yellow-400 font-semibold mb-2">Lesson not found</p>
            <p className="text-yellow-500/70 text-sm mb-4">
              The lesson you're looking for doesn't exist or hasn't loaded properly.
            </p>
            <p className="text-zinc-500 text-sm">Lesson ID: {id}</p>
          </div>
          <button
            onClick={() => navigate('/lessons')}
            className="px-4 py-2 bg-orange-500 text-white font-bold uppercase tracking-widest hover:bg-orange-600"
          >
            Back to Lessons
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-950">
      {/* Header */}
      <div className="bg-zinc-950 border-b border-zinc-800 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/lessons')}
                className="p-2 hover:bg-zinc-800 transition-colors"
              >
                <ArrowLeftIcon className="w-5 h-5 text-zinc-400" />
              </button>
              <div>
                <h1 className="text-2xl font-black text-white uppercase tracking-tight">{lesson.title}</h1>
                <div className="flex items-center gap-3 mt-1 text-sm text-zinc-500">
                  <div className="flex items-center gap-1">
                    <ClockIcon className="w-4 h-4" />
                    {lesson.duration_minutes} min
                  </div>
                  <span className={`px-2 py-0.5 text-xs font-bold uppercase tracking-widest border ${
                    lesson.difficulty === 'beginner' ? 'border-green-700 text-green-400' :
                    lesson.difficulty === 'intermediate' ? 'border-yellow-700 text-yellow-400' :
                    'border-red-700 text-red-400'
                  }`}>
                    {lesson.difficulty}
                  </span>
                  <span className="px-2 py-0.5 text-xs font-bold uppercase tracking-widest border border-zinc-700 text-zinc-400 capitalize">
                    {lesson.category.replace('_', ' ')}
                  </span>
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <button
                onClick={() => completeLessonMutation.mutate()}
                disabled={isCompleting}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white font-bold uppercase tracking-widest hover:bg-green-700 disabled:opacity-50 transition-colors"
              >
                {isCompleting ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <CheckCircleIcon className="w-4 h-4" />
                    Complete
                  </>
                )}
              </button>
              
              <Link
                to={`/lessons/${id}/quiz`}
                className="flex items-center gap-2 px-4 py-2 bg-orange-500 text-white font-bold uppercase tracking-widest hover:bg-orange-600 transition-colors"
              >
                <AcademicCapIcon className="w-4 h-4" />
                Take Quiz
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-5xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content - 2/3 width */}
          <div className="lg:col-span-2 space-y-4">
            {contentCards.map((card, index) => (
              <div key={index}>
                {card.type === 'heading' && (
                  <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl p-6 shadow-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-zinc-900/20 rounded-lg flex items-center justify-center">
                        <SparklesIcon className="w-6 h-6" />
                      </div>
                      <h2 className="text-2xl font-bold">{card.content}</h2>
                    </div>
                  </div>
                )}
                
                {card.type === 'paragraph' && (
                  <div className="bg-zinc-900 p-6 border border-zinc-800">
                    <p className="text-zinc-300 leading-relaxed">{card.content}</p>
                  </div>
                )}
                
                {card.type === 'list' && card.items && (
                  <div className="bg-zinc-900 p-6 border border-zinc-800">
                    <ul className="space-y-3">
                      {card.items.map((item, i) => (
                        <li key={i} className="flex items-start gap-3">
                          <div className="flex-shrink-0 w-2 h-2 bg-orange-500 mt-2" />
                          <span className="text-zinc-300 flex-1">{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Sidebar - 1/3 width */}
          <div className="lg:col-span-1">
            <div className="sticky top-24 space-y-4">
              {/* Quick Info Card */}
              <div className="bg-zinc-900 p-6 border border-zinc-800">
                <h3 className="font-black text-white mb-4 flex items-center gap-2 uppercase tracking-widest text-sm">
                  <LightBulbIcon className="w-5 h-5 text-orange-500" />
                  Quick Info
                </h3>
                <div className="space-y-3 text-sm">
                  <div>
                    <span className="font-semibold text-zinc-400 uppercase tracking-widest text-xs">Duration</span>
                    <p className="text-white font-bold">{lesson.duration_minutes} minutes</p>
                  </div>
                  <div>
                    <span className="font-semibold text-zinc-400 uppercase tracking-widest text-xs">Difficulty</span>
                    <p className="text-white font-bold capitalize">{lesson.difficulty}</p>
                  </div>
                  <div>
                    <span className="font-semibold text-zinc-400 uppercase tracking-widest text-xs">Category</span>
                    <p className="text-white font-bold capitalize">{lesson.category.replace('_', ' ')}</p>
                  </div>
                  <div>
                    <span className="font-semibold text-zinc-400 uppercase tracking-widest text-xs">Type</span>
                    <p className="text-white font-bold capitalize">{lesson.lesson_type}</p>
                  </div>
                </div>
              </div>

              {/* Tips Card */}
              <div className="bg-zinc-900 p-6 border border-purple-900/40">
                <h3 className="font-black text-white mb-3 flex items-center gap-2 uppercase tracking-widest text-sm">
                  <SparklesIcon className="w-5 h-5 text-purple-400" />
                  Study Tips
                </h3>
                <ul className="space-y-2 text-sm text-zinc-400">
                  <li className="flex items-start gap-2">
                    <span className="text-purple-400">—</span>
                    <span>Take notes as you read</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-purple-400">—</span>
                    <span>Practice the concepts</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-purple-400">—</span>
                    <span>Complete the quiz to test your knowledge</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-purple-400">—</span>
                    <span>Review difficult sections</span>
                  </li>
                </ul>
              </div>

              {/* Action Card */}
              <div className="bg-gradient-to-br from-blue-600 to-blue-700 text-white p-6">
                <h3 className="font-black mb-3 uppercase tracking-tight">Ready to test your knowledge?</h3>
                <p className="text-sm text-blue-200 mb-4">
                  Take the quiz to earn points and track your progress!
                </p>
                <Link
                  to={`/lessons/${id}/quiz`}
                  className="block w-full py-3 bg-zinc-900 text-blue-600 font-black uppercase tracking-widest text-center hover:bg-blue-50 transition-colors"
                >
                  Start Quiz
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
