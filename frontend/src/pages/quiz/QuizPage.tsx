import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { apiClient, progressApi, lessonsApi } from '@/services/api';
import { useAuthStore } from '@/stores/useAuthStore';
import { 
  CheckCircleIcon, 
  XCircleIcon, 
  ClockIcon,
  QuestionMarkCircleIcon,
  LightBulbIcon
} from '@heroicons/react/24/outline';

interface QuizQuestion {
  id: string;
  question: string;
  options: string[];
  correct_answer: number;
  explanation: string;
  difficulty: 'easy' | 'medium' | 'hard';
  question_type?: string;
}

interface QuizData {
  lesson_id: string;
  questions: QuizQuestion[];
  total_questions: number;
}

export function QuizPage() {
  const { lessonId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuthStore();
  
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, number>>({});
  const [showResults, setShowResults] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(900); // 15 minutes
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Fetch lesson data for the title
  const { data: lessonResponse } = useQuery({
    queryKey: ['lesson', lessonId],
    queryFn: () => lessonsApi.getById(lessonId!),
    enabled: !!lessonId,
  });

  const lessonTitle = lessonResponse?.data?.title;

  // Fetch quiz data from API
  const { data: quizResponse, isLoading, error } = useQuery({
    queryKey: ['quiz', lessonId],
    queryFn: async () => {
      const response = await apiClient.get<QuizData>(`/lessons/${lessonId}/quiz`);
      return response.data;
    },
    enabled: !!lessonId,
  });

  const quizData = quizResponse?.questions || [];

  // Submit quiz mutation
  const submitQuizMutation = useMutation({
    mutationFn: async (answers: Record<number, number>) => {
      // Calculate score
      const correctAnswers = quizData.reduce((count, question, index) => {
        return count + (answers[index] === question.correct_answer ? 1 : 0);
      }, 0);
      
      const score = Math.round((correctAnswers / quizData.length) * 100);
      
      // Submit to backend
      try {
        await progressApi.updateProgress(lessonId!, {
          completion_status: 'completed',
          score: score
        });
      } catch (error) {
        console.error('Error submitting quiz:', error);
        // Continue anyway - we calculated the score locally
      }
      
      return { score, correctAnswers, totalQuestions: quizData.length };
    },
    onSuccess: (data) => {
      console.log('Quiz submitted successfully:', data);
      setIsSubmitting(false);
      setShowResults(true);
    },
    onError: (error) => {
      console.error('Quiz submission error:', error);
      // Show results anyway with locally calculated score
      setIsSubmitting(false);
      setShowResults(true);
    }
  });

  // Timer effect
  useEffect(() => {
    if (timeRemaining > 0 && !showResults) {
      const timer = setTimeout(() => setTimeRemaining(timeRemaining - 1), 1000);
      return () => clearTimeout(timer);
    } else if (timeRemaining === 0) {
      handleSubmitQuiz();
    }
  }, [timeRemaining, showResults]);

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const handleAnswerSelect = (answerIndex: number) => {
    setSelectedAnswers(prev => ({
      ...prev,
      [currentQuestion]: answerIndex
    }));
  };

  const handleNext = () => {
    if (currentQuestion < quizData.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const handleSubmitQuiz = () => {
    if (isSubmitting) return; // Prevent double submission
    setIsSubmitting(true);
    submitQuizMutation.mutate(selectedAnswers);
  };

  const calculateResults = () => {
    if (submitQuizMutation.data) {
      return submitQuizMutation.data;
    }
    
    // Fallback: calculate locally if mutation data is not available
    const correctAnswers = quizData.reduce((count, question, index) => {
      return count + (selectedAnswers[index] === question.correct_answer ? 1 : 0);
    }, 0);
    
    const score = Math.round((correctAnswers / quizData.length) * 100);
    
    return { score, correctAnswers, totalQuestions: quizData.length };
  };

  const getAnswerIcon = (questionIndex: number, optionIndex: number) => {
    if (!showResults) return null;
    
    const question = quizData[questionIndex];
    const userAnswer = selectedAnswers[questionIndex];
    const correctAnswer = question.correct_answer;
    
    if (optionIndex === correctAnswer) {
      return <CheckCircleIcon className="h-5 w-5 text-green-600" />;
    } else if (optionIndex === userAnswer && userAnswer !== correctAnswer) {
      return <XCircleIcon className="h-5 w-5 text-red-600" />;
    }
    return null;
  };

  const getOptionClassName = (questionIndex: number, optionIndex: number) => {
    if (!showResults) {
      const isSelected = selectedAnswers[currentQuestion] === optionIndex;
      return `p-4 border rounded-none cursor-pointer transition-colors ${
        isSelected 
          ? 'border-orange-500 bg-orange-500/10 text-zinc-100' 
          : 'border-zinc-700 hover:border-orange-500 hover:bg-zinc-800 text-zinc-300'
      }`;
    }
    
    const question = quizData[questionIndex];
    const userAnswer = selectedAnswers[questionIndex];
    const correctAnswer = question.correct_answer;
    
    if (optionIndex === correctAnswer) {
      return 'p-4 border border-green-500 bg-green-950/40 rounded-none text-zinc-200';
    } else if (optionIndex === userAnswer && userAnswer !== correctAnswer) {
      return 'p-4 border border-red-500 bg-red-950/40 rounded-none text-zinc-200';
    } else {
      return 'p-4 border border-zinc-700 bg-zinc-800 rounded-none text-zinc-400';
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="px-4 sm:px-6 lg:px-8 py-12">
        <div className="max-w-2xl mx-auto text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto"></div>
          <p className="mt-4 text-zinc-400 uppercase tracking-widest text-sm">Loading quiz...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="px-4 sm:px-6 lg:px-8 py-12">
        <div className="max-w-2xl mx-auto text-center">
          <XCircleIcon className="h-12 w-12 text-red-500 mx-auto" />
          <h2 className="mt-4 text-xl font-black uppercase text-zinc-100">Quiz Not Available</h2>
          <p className="mt-2 text-zinc-400">This lesson doesn't have a quiz yet.</p>
          <button
            onClick={() => navigate('/lessons')}
            className="mt-6 px-4 py-2 bg-orange-500 text-black font-bold uppercase tracking-widest hover:bg-orange-400"
          >
            Back to Lessons
          </button>
        </div>
      </div>
    );
  }

  // No questions
  if (!quizData || quizData.length === 0) {
    return (
      <div className="px-4 sm:px-6 lg:px-8 py-12">
        <div className="max-w-2xl mx-auto text-center">
          <QuestionMarkCircleIcon className="h-12 w-12 text-zinc-500 mx-auto" />
          <h2 className="mt-4 text-xl font-black uppercase text-zinc-100">No Questions Available</h2>
          <p className="mt-2 text-zinc-400">This quiz doesn't have any questions yet.</p>
          <button
            onClick={() => navigate('/lessons')}
            className="mt-6 px-4 py-2 bg-orange-500 text-black font-bold uppercase tracking-widest hover:bg-orange-400"
          >
            Back to Lessons
          </button>
        </div>
      </div>
    );
  }

  if (showResults) {
    const results = calculateResults();

    return (
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-2xl font-black uppercase text-zinc-100">Quiz Results</h1>
          <p className="mt-1 text-sm text-zinc-400 uppercase tracking-widest">
            Review your answers and explanations.
          </p>
        </div>

        {/* Results Summary */}
        <div className="bg-zinc-900 border border-zinc-800 p-6 mb-6">
          <div className="text-center">
            <div className={`inline-flex items-center px-4 py-2 text-lg font-black uppercase tracking-widest border ${
              results.score >= 70 ? 'bg-green-950/40 border-green-600 text-green-400' : 'bg-red-950/40 border-red-600 text-red-400'
            }`}>
              {results.score >= 70 ? (
                <CheckCircleIcon className="h-6 w-6 mr-2" />
              ) : (
                <XCircleIcon className="h-6 w-6 mr-2" />
              )}
              Score: {results.score}%
            </div>
            <p className="mt-2 text-zinc-400">
              You got {results.correctAnswers} out of {results.totalQuestions} questions correct.
            </p>
            <div className="mt-4 flex justify-center space-x-4">
              <button
                onClick={() => navigate('/lessons')}
                className="px-4 py-2 bg-orange-500 text-black font-bold uppercase tracking-widest hover:bg-orange-400 transition-colors"
              >
                Back to Lessons
              </button>
              <button
                onClick={() => window.location.reload()}
                className="px-4 py-2 border border-zinc-700 text-zinc-300 hover:bg-zinc-800 hover:border-zinc-500 transition-colors uppercase tracking-widest font-bold"
              >
                Retake Quiz
              </button>
            </div>
          </div>
        </div>

        {/* Question Review */}
        <div className="space-y-6">
          {quizData.map((question, questionIndex) => (
            <div key={question.id} className="bg-zinc-900 border border-zinc-800 p-6">
              <div className="flex items-start justify-between mb-4">
                <h3 className="text-lg font-black uppercase text-zinc-100">
                  Question {questionIndex + 1}
                </h3>
                <span className={`px-2 py-1 text-xs font-bold uppercase tracking-widest border ${
                  question.difficulty === 'easy' ? 'bg-green-950/40 border-green-700 text-green-400' :
                  question.difficulty === 'medium' ? 'bg-yellow-950/40 border-yellow-700 text-yellow-400' :
                  'bg-red-950/40 border-red-700 text-red-400'
                }`}>
                  {question.difficulty}
                </span>
              </div>
              
              <p className="text-zinc-200 mb-4">{question.question}</p>
              
              <div className="space-y-2 mb-4">
                {question.options.map((option, optionIndex) => (
                  <div key={optionIndex} className={getOptionClassName(questionIndex, optionIndex)}>
                    <div className="flex items-center justify-between">
                      <span className="text-zinc-200">{option}</span>
                      {getAnswerIcon(questionIndex, optionIndex)}
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="bg-zinc-800 border border-zinc-700 p-4">
                <div className="flex items-start">
                  <LightBulbIcon className="h-5 w-5 text-orange-500 mt-0.5 mr-2 flex-shrink-0" />
                  <div>
                    <h4 className="text-sm font-black uppercase tracking-widest text-zinc-200">Explanation</h4>
                    <p className="text-sm text-zinc-300 mt-1">{question.explanation}</p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  const currentQuestionData = quizData[currentQuestion];
  const progress = ((currentQuestion + 1) / quizData.length) * 100;

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-black uppercase text-zinc-100">
              {lessonTitle ? `${lessonTitle} Quiz` : 'Quiz'}
            </h1>
            <p className="mt-1 text-sm text-zinc-400 uppercase tracking-widest">
              Question {currentQuestion + 1} of {quizData.length}
            </p>
          </div>
          <div className="flex items-center text-sm text-zinc-400 font-mono">
            <ClockIcon className="h-4 w-4 mr-1 text-orange-500" />
            {formatTime(timeRemaining)}
          </div>
        </div>
        
        {/* Progress Bar */}
        <div className="mt-4">
          <div className="w-full bg-zinc-800 h-2">
            <div 
              className="bg-orange-500 h-2 transition-all duration-300"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>
      </div>

      <div className="bg-zinc-900 border border-zinc-800 p-6">
        {/* Question */}
        <div className="mb-6">
          <div className="flex items-start justify-between mb-4">
            <h2 className="text-xl font-black uppercase text-zinc-100">
              Question {currentQuestion + 1}
            </h2>
            <span className={`px-2 py-1 text-xs font-bold uppercase tracking-widest border ${
              currentQuestionData.difficulty === 'easy' ? 'bg-green-950/40 border-green-700 text-green-400' :
              currentQuestionData.difficulty === 'medium' ? 'bg-yellow-950/40 border-yellow-700 text-yellow-400' :
              'bg-red-950/40 border-red-700 text-red-400'
            }`}>
              {currentQuestionData.difficulty}
            </span>
          </div>
          <p className="text-lg text-zinc-200">{currentQuestionData.question}</p>
        </div>

        {/* Answer Options */}
        <div className="space-y-3 mb-8">
          {currentQuestionData.options.map((option, index) => (
            <button
              key={index}
              onClick={() => handleAnswerSelect(index)}
              className={getOptionClassName(currentQuestion, index)}
            >
              <div className="flex items-center">
                <div className={`w-4 h-4 rounded-full border-2 mr-3 ${
                  selectedAnswers[currentQuestion] === index
                    ? 'border-orange-500 bg-orange-500'
                    : 'border-zinc-600'
                }`}>
                  {selectedAnswers[currentQuestion] === index && (
                    <div className="w-2 h-2 rounded-full bg-white mx-auto mt-0.5"></div>
                  )}
                </div>
                <span className="text-left">{option}</span>
              </div>
            </button>
          ))}
        </div>

        {/* Navigation */}
        <div className="flex justify-between items-center">
          <button
            onClick={handlePrevious}
            disabled={currentQuestion === 0}
            className="px-4 py-2 text-sm font-bold uppercase tracking-widest text-zinc-300 bg-zinc-800 border border-zinc-700 hover:bg-zinc-700 hover:border-zinc-500 disabled:opacity-30 disabled:cursor-not-allowed"
          >
            Previous
          </button>

          <div className="flex space-x-3">
            {currentQuestion === quizData.length - 1 ? (
              <button
                onClick={handleSubmitQuiz}
                disabled={Object.keys(selectedAnswers).length !== quizData.length || isSubmitting}
                className="px-6 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                {isSubmitting ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Submitting...
                  </>
                ) : (
                  <>
                    <CheckCircleIcon className="h-4 w-4 mr-2" />
                    Submit Quiz
                  </>
                )}
              </button>
            ) : (
              <button
                onClick={handleNext}
                disabled={selectedAnswers[currentQuestion] === undefined}
                className="px-4 py-2 text-sm font-black uppercase tracking-widest text-black bg-orange-500 hover:bg-orange-400 disabled:opacity-30 disabled:cursor-not-allowed"
              >
                Next
              </button>
            )}
          </div>
        </div>

        {/* Quiz Info */}
        <div className="mt-6 p-4 bg-zinc-800 border border-zinc-700">
          <div className="flex items-center text-sm text-zinc-400">
            <QuestionMarkCircleIcon className="h-4 w-4 mr-2 text-zinc-500" />
            <span>
              Answer all questions to submit. You can go back and change your answers before submitting.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}






