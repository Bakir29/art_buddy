import React, { useState, useMemo, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import { lessonsApi, progressApi } from '@/services/api';
import { useAuthStore } from '@/stores/useAuthStore';
import { Progress } from '@/types';
import {
  LockClosedIcon,
  CheckCircleIcon,
  FireIcon,
  TrophyIcon,
  StarIcon
} from '@heroicons/react/24/solid';
import {
  PaintBrushIcon,
  PencilIcon,
  SparklesIcon,
  ComputerDesktopIcon,
  Squares2X2Icon,
  UserCircleIcon,
  CubeIcon
} from '@heroicons/react/24/outline';

interface LessonData {
  id: string;
  title: string;
  content: string;
  difficulty: string;
  category: string;
  order_in_category: number;
  lesson_type: string;
  duration_minutes: number;
  prerequisites: string[];
  is_active: boolean;
}

const CATEGORY_INFO: Record<string, {
  name: string;
  icon: React.ElementType;
  color: string;
  gradient: string;
  lightBg: string;
}> = {
  drawing: {
    name: 'Drawing',
    icon: PencilIcon,
    color: '#3B82F6',
    gradient: 'from-blue-400 to-blue-600',
    lightBg: 'bg-blue-950/30'
  },
  painting: {
    name: 'Painting',
    icon: PaintBrushIcon,
    color: '#A855F7',
    gradient: 'from-purple-400 to-purple-600',
    lightBg: 'bg-purple-950/30'
  },
  color_theory: {
    name: 'Color Theory',
    icon: SparklesIcon,
    color: '#EC4899',
    gradient: 'from-pink-400 to-pink-600',
    lightBg: 'bg-pink-950/30'
  },
  digital_art: {
    name: 'Digital Art',
    icon: ComputerDesktopIcon,
    color: '#6366F1',
    gradient: 'from-indigo-400 to-indigo-600',
    lightBg: 'bg-indigo-950/30'
  },
  design: {
    name: 'Design',
    icon: Squares2X2Icon,
    color: '#10B981',
    gradient: 'from-green-400 to-green-600',
    lightBg: 'bg-emerald-950/30'
  },
  character_art: {
    name: 'Character Art',
    icon: UserCircleIcon,
    color: '#F59E0B',
    gradient: 'from-orange-400 to-orange-600',
    lightBg: 'bg-orange-950/30'
  },
  sculpture: {
    name: 'Sculpture',
    icon: CubeIcon,
    color: '#78716C',
    gradient: 'from-stone-400 to-stone-600',
    lightBg: 'bg-stone-950/30'
  }
};

const LessonNode = React.memo(function LessonNode({ 
  lesson, 
  progress, 
  isLocked,
  position,
  categoryColor,
  onStart 
}: {
  lesson: LessonData;
  progress?: Progress;
  isLocked: boolean;
  position: 'left' | 'center' | 'right';
  categoryColor: string;
  onStart: () => void;
}) {
  const navigate = useNavigate();
  const isCompleted = progress?.completion_status === 'completed';
  const isInProgress = progress?.completion_status === 'in_progress';

  const positionClasses = {
    left: 'ml-8',
    center: 'mx-auto',
    right: 'mr-8 ml-auto'
  };

  const handleClick = () => {
    if (isLocked) return;
    if (isCompleted) {
      navigate(`/lessons/${lesson.id}/quiz`);
    } else {
      onStart();
    }
  };

  return (
    <div className={`relative flex flex-col items-center ${positionClasses[position]} w-32`}>
      {/* Lesson Node */}
      <button
        onClick={handleClick}
        disabled={isLocked}
        className={`relative group transition-all duration-300 ${
          isLocked ? 'cursor-not-allowed' : 'cursor-pointer hover:scale-110'
        }`}
      >
        {/* Outer Circle with Gradient Border */}
        <div className={`w-20 h-20 rounded-full p-1 ${
          isCompleted 
            ? 'bg-gradient-to-br from-yellow-400 to-yellow-600' 
            : isInProgress
            ? `bg-gradient-to-br ${CATEGORY_INFO[lesson.category]?.gradient || 'from-gray-400 to-gray-600'}`
            : isLocked
            ? 'bg-gradient-to-br from-zinc-700 to-zinc-600'
            : 'bg-gradient-to-br from-zinc-600 to-zinc-500 group-hover:from-orange-400 group-hover:to-orange-600'
        }`}>
          {/* Inner Circle */}
          <div className={`w-full h-full rounded-full flex items-center justify-center ${
            isCompleted 
              ? 'bg-zinc-950' 
              : isInProgress
              ? 'bg-zinc-950'
              : 'bg-zinc-950'
          }`}>
            {isCompleted ? (
              <CheckCircleIcon className="w-10 h-10 text-yellow-600" />
            ) : isLocked ? (
              <LockClosedIcon className="w-8 h-8 text-gray-400" />
            ) : isInProgress ? (
              <div className="w-8 h-8 rounded-full border-4 border-t-transparent animate-spin" 
                   style={{ borderColor: categoryColor, borderTopColor: 'transparent' }} />
            ) : (
              <StarIcon className="w-10 h-10 text-zinc-600 group-hover:text-orange-400" />
            )}
          </div>
        </div>

        {/* Completion Score Badge */}
        {isCompleted && progress?.score_percentage && (
          <div className="absolute -top-1 -right-1 w-7 h-7 rounded-full bg-green-500 text-white text-xs font-bold flex items-center justify-center border-2 border-zinc-950 shadow-lg">
            {Math.round(progress.score_percentage)}
          </div>
        )}

        {/* Order Number */}
        <div className="absolute -top-2 -left-2 w-6 h-6 rounded-full bg-zinc-700 text-white text-xs font-bold flex items-center justify-center border-2 border-zinc-950">
          {lesson.order_in_category}
        </div>
      </button>

      {/* Lesson Title */}
      <div className="mt-3 text-center">
        <h3 className={`text-sm font-bold ${
          isCompleted ? 'text-white' : isLocked ? 'text-zinc-600' : 'text-zinc-300'
        }`}>
          {lesson.title}
        </h3>
        <p className="text-xs text-zinc-500 mt-1">{lesson.duration_minutes} min</p>
        
        {/* Action Buttons */}
        {!isLocked && (
          <div className="mt-2 flex gap-1 justify-center">
            {!isCompleted && (
              <button
                onClick={(e) => { e.stopPropagation(); onStart(); }}
                className="px-3 py-1 text-xs font-semibold rounded-full bg-green-500 text-white hover:bg-green-600 transition-colors"
              >
                {isInProgress ? 'Continue' : 'Start'}
              </button>
            )}
            <Link
              to={`/lessons/${lesson.id}/quiz`}
              onClick={(e) => e.stopPropagation()}
              className="px-3 py-1 text-xs font-semibold rounded-full bg-purple-500 text-white hover:bg-purple-600 transition-colors"
            >
              Quiz
            </Link>
          </div>
        )}
      </div>
    </div>
  );
});

const PathConnector = React.memo(function PathConnector({ categoryColor }: { categoryColor: string }) {
  return (
    <div className="w-1 h-12 mx-auto" style={{ backgroundColor: categoryColor, opacity: 0.3 }} />
  );
});

const CategoryCard = React.memo(function CategoryCard({ 
  category, 
  lessons, 
  completedCount,
  onSelect 
}: {
  category: string;
  lessons: LessonData[];
  completedCount: number;
  onSelect: () => void;
}) {
  const info = CATEGORY_INFO[category] || CATEGORY_INFO.drawing;
  const Icon = info.icon;
  const progress = lessons.length > 0 ? Math.round((completedCount / lessons.length) * 100) : 0;

  return (
    <button
      onClick={onSelect}
      className="w-full bg-zinc-900 transition-all duration-200 p-6 border border-zinc-800 hover:border-orange-500 group"
    >
      <div className="flex items-center gap-4 mb-4">
        <div className={`w-16 h-16 bg-gradient-to-br ${info.gradient} flex items-center justify-center group-hover:opacity-90 transition-opacity`}>
          <Icon className="w-9 h-9 text-white" />
        </div>
        <div className="flex-1 text-left">
          <h3 className="text-2xl font-black text-white group-hover:text-orange-400 transition-colors uppercase tracking-tight">
            {info.name}
          </h3>
          <p className="text-sm text-zinc-500">{lessons.length} lessons</p>
        </div>
        <div className="text-right">
          <div className="text-3xl font-black" style={{ color: info.color }}>
            {progress}%
          </div>
          <p className="text-xs text-zinc-500 uppercase tracking-widest">complete</p>
        </div>
      </div>
      
      {/* Progress Bar */}
      <div className="w-full h-2 bg-zinc-800 overflow-hidden">
        <div 
          className={`h-full bg-gradient-to-r ${info.gradient} transition-all duration-500`}
          style={{ width: `${progress}%` }}
        />
      </div>
      
      {/* Stats */}
      <div className="mt-4 flex items-center justify-between text-sm">
        <span className="text-zinc-500">
          {completedCount} of {lessons.length} completed
        </span>
        {completedCount === lessons.length && lessons.length > 0 && (
          <div className="flex items-center gap-1 text-yellow-500">
            <CheckCircleIcon className="w-5 h-5" />
            <span className="font-semibold">Mastered!</span>
          </div>
        )}
      </div>
    </button>
  );
});

export function LessonsPage() {
  const { user } = useAuthStore();
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  const { data: lessons, isLoading: lessonsLoading } = useQuery({
    queryKey: ['lessons'],
    queryFn: () => lessonsApi.getAll(),
    staleTime: 0, // Always background-revalidate so the full 70-lesson list is fresh
    gcTime: 1000 * 60 * 10, // 10 minutes
  });

  const { data: progressData } = useQuery({
    queryKey: ['progress', user?.id],
    queryFn: () => progressApi.getUserProgress(user?.id),
    enabled: !!user,
    staleTime: 0,
    refetchOnMount: 'always', // Always hit the server on mount regardless of cache freshness
    gcTime: Infinity, // Never evict: ensures cached data survives long lesson reads
  });

  const updateProgressMutation = useMutation({
    mutationFn: async ({ lessonId, status }: { lessonId: string; status: string }) => {
      if (status === 'in_progress') {
        return progressApi.startLesson(lessonId);
      } else {
        return progressApi.updateProgress(lessonId, {
          completion_status: 'completed',
          score: 85
        });
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['progress'] });
    },
  });

  const progressMap = useMemo(() => {
    if (!progressData) return {};
    const data = Array.isArray(progressData) ? progressData : (progressData as any)?.data;
    if (!data) return {};
    const map: Record<string, Progress> = {};
    data.forEach((p: Progress) => {
      map[p.lesson_id] = p;
    });
    return map;
  }, [progressData]);

  const lessonsByCategory = useMemo(() => {
    if (!lessons) return {};
    const grouped: Record<string, LessonData[]> = {};
    lessons.forEach((lesson: LessonData) => {
      const cat = lesson.category || 'general';
      if (!grouped[cat]) grouped[cat] = [];
      grouped[cat].push(lesson);
    });
    Object.keys(grouped).forEach(cat => {
      grouped[cat].sort((a, b) => a.order_in_category - b.order_in_category);
    });
    return grouped;
  }, [lessons]);

  const categories = Object.keys(lessonsByCategory).sort();

  // Calculate if lesson is locked - useCallback to prevent recreation
  const isLessonLocked = useCallback((lesson: LessonData): boolean => {
    if (lesson.order_in_category === 1) return false;
    const categoryLessons = lessonsByCategory[lesson.category] || [];
    const prevLesson = categoryLessons.find(l => l.order_in_category === lesson.order_in_category - 1);
    if (!prevLesson) return false;
    const prevProgress = progressMap[prevLesson.id];
    return prevProgress?.completion_status !== 'completed';
  }, [lessonsByCategory, progressMap]);

  const totalCompleted = Object.values(progressMap).filter(p => p.completion_status === 'completed').length;
  const totalLessons = lessons?.length || 0;
  const overallProgress = totalLessons > 0 ? Math.round((totalCompleted / totalLessons) * 100) : 0;

  if (lessonsLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-zinc-950">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-orange-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-zinc-500">Loading your learning path...</p>
        </div>
      </div>
    );
  }

  // CATEGORY SELECTION VIEW (like Duolingo language selection)
  if (!selectedCategory) {
    return (
      <div className="min-h-screen bg-zinc-950">
        {/* Header */}
        <div className="bg-zinc-950 border-b border-zinc-800">
          <div className="max-w-4xl mx-auto px-4 py-6">
            <div className="text-center mb-4">
              <h1 className="text-3xl font-black tracking-tight text-white uppercase mb-2">Choose Your Subject</h1>
              <p className="text-zinc-500">Select a category to start learning</p>
            </div>
            
            {/* Overall Stats */}
            <div className="flex items-center justify-center gap-4">
              <div className="flex items-center gap-2 bg-zinc-900 border border-zinc-800 px-4 py-2">
                <FireIcon className="w-4 h-4 text-orange-500" />
                <span className="font-bold text-zinc-300 text-sm">0 day streak</span>
              </div>
              <div className="flex items-center gap-2 bg-zinc-900 border border-zinc-800 px-4 py-2">
                <TrophyIcon className="w-4 h-4 text-yellow-500" />
                <span className="font-bold text-zinc-300 text-sm">{totalCompleted} lessons</span>
              </div>
              <div className="flex items-center gap-2 bg-zinc-900 border border-zinc-800 px-4 py-2">
                <StarIcon className="w-4 h-4 text-orange-400" />
                <span className="font-bold text-zinc-300 text-sm">{overallProgress}% overall</span>
              </div>
            </div>
          </div>
        </div>

        {/* Category Cards Grid */}
        <div className="max-w-4xl mx-auto px-4 py-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {categories.map((category) => {
              const categoryLessons = lessonsByCategory[category];
              const completedInCategory = categoryLessons.filter(
                l => progressMap[l.id]?.completion_status === 'completed'
              ).length;

              return (
                <CategoryCard
                  key={category}
                  category={category}
                  lessons={categoryLessons}
                  completedCount={completedInCategory}
                  onSelect={() => setSelectedCategory(category)}
                />
              );
            })}
          </div>
        </div>
      </div>
    );
  }

  // CATEGORY LESSONS VIEW (showing lessons for selected category)
  const categoryLessons = lessonsByCategory[selectedCategory] || [];
  const completedInCategory = categoryLessons.filter(
    l => progressMap[l.id]?.completion_status === 'completed'
  ).length;
  const categoryInfo = CATEGORY_INFO[selectedCategory] || CATEGORY_INFO.drawing;
  const categoryProgress = categoryLessons.length > 0 
    ? Math.round((completedInCategory / categoryLessons.length) * 100) 
    : 0;

  return (
    <div className="min-h-screen bg-zinc-950">
      {/* Header with Back Button */}
      <div className="bg-zinc-900 border-b border-zinc-800 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <button
            onClick={() => setSelectedCategory(null)}
            className="flex items-center gap-2 text-zinc-400 hover:text-white font-semibold mb-3 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Categories
          </button>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`w-12 h-12 bg-gradient-to-br ${categoryInfo.gradient} flex items-center justify-center`}>
                <categoryInfo.icon className="w-7 h-7 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-black text-white uppercase tracking-tight">{categoryInfo.name}</h1>
                <p className="text-sm text-zinc-500">{categoryLessons.length} lessons</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 bg-zinc-800 border border-zinc-700 px-4 py-2">
                <TrophyIcon className="w-5 h-5 text-yellow-500" />
                <span className="font-bold text-yellow-400">{completedInCategory}/{categoryLessons.length}</span>
              </div>
            </div>
          </div>
          
          {/* Category Progress */}
          <div className="mt-4 bg-zinc-800 h-2 overflow-hidden">
            <div 
              className={`h-full bg-gradient-to-r ${categoryInfo.gradient} transition-all duration-500`}
              style={{ width: `${categoryProgress}%` }}
            />
          </div>
          <p className="text-xs text-zinc-500 mt-1 uppercase tracking-widest">{categoryProgress}% Complete</p>
        </div>
      </div>

      {/* Learning Path for Selected Category */}
      <div className="max-w-2xl mx-auto px-4 py-8 pb-20">
        <div className="relative">
          {categoryLessons.map((lesson, index) => {
            const position = index % 3 === 0 ? 'center' : index % 3 === 1 ? 'left' : 'right';
            const handleStartLesson = () => {
              // Start lesson and navigate to lesson detail
              navigate(`/lessons/${lesson.id}`);
              // Also mark as in progress if not already
              if (!progressMap[lesson.id] || progressMap[lesson.id].completion_status === 'not_started') {
                updateProgressMutation.mutate({ 
                  lessonId: lesson.id, 
                  status: 'in_progress'
                });
              }
            };
            
            return (
              <div key={lesson.id}>
                <LessonNode
                  lesson={lesson}
                  progress={progressMap[lesson.id]}
                  isLocked={isLessonLocked(lesson)}
                  position={position}
                  categoryColor={categoryInfo.color}
                  onStart={handleStartLesson}
                />
                {index < categoryLessons.length - 1 && (
                  <PathConnector categoryColor={categoryInfo.color} />
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
