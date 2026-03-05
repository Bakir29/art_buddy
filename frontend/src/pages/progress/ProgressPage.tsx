import { useState } from 'react';
import toast from 'react-hot-toast';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { progressApi, workflowsApi, mcpApi } from '@/services/api';
import { formatDate } from '@/utils';
import { useAuthStore } from '@/stores/useAuthStore';
import {
  ChartBarIcon,
  CalendarIcon,
  TrophyIcon,
  FireIcon,
  ClockIcon,
  BookOpenIcon,
  LightBulbIcon,
  CogIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';

export function ProgressPage() {
  const { user } = useAuthStore();
  const queryClient = useQueryClient();
  const [workflowTesting, setWorkflowTesting] = useState<Record<string, boolean>>({});
  const [mcpResult, setMcpResult] = useState<{ tool: string; data: any } | null>(null);

  // Fetch progress summary
  const { data: progressSummary } = useQuery({
    queryKey: ['progress', 'summary'],
    queryFn: () => progressApi.getSummary(),
    refetchOnWindowFocus: false,
  });

  // Fetch detailed progress (cached for child components)
  useQuery({
    queryKey: ['progress', 'detailed'],
    queryFn: () => progressApi.getUserProgress(user?.id),
    enabled: !!user?.id,
    refetchOnWindowFocus: false,
  });

  // Get MCP tools (cached for child components)
  useQuery({
    queryKey: ['mcp', 'tools'],
    queryFn: () => mcpApi.getAvailableTools(),
    refetchOnWindowFocus: false,
  });

  // Workflow trigger mutation — maps workflow type to the correct simulate endpoint
  const triggerWorkflowMutation = useMutation({
    mutationFn: ({ workflowType, data }: { workflowType: string; data: any }) => {
      switch (workflowType) {
        case 'daily_practice_reminder':
          return workflowsApi.simulateDailyReminder();
        case 'low_performance_intervention':
          return workflowsApi.simulateLowPerformance();
        case 'weekly_progress_summary':
          return workflowsApi.simulateWeeklySummary();
        case 'lesson_completion_handler':
          return workflowsApi.simulateLessonCompletion({ lesson_id: data?.lesson_id || 'test-completion', score: data?.score });
        default:
          return workflowsApi.simulateDailyReminder();
      }
    },
    onMutate: ({ workflowType }) => {
      setWorkflowTesting(prev => ({ ...prev, [workflowType]: true }));
    },
    onSuccess: (_result: any, { workflowType }) => {
      toast.success(`Workflow "${workflowType}" triggered — notification sent!`);
    },
    onError: (_err: any, { workflowType }) => {
      toast.error(`Failed to trigger workflow "${workflowType}"`);
    },
    onSettled: (_, __, { workflowType }) => {
      setTimeout(() => {
        setWorkflowTesting(prev => ({ ...prev, [workflowType]: false }));
        queryClient.invalidateQueries({ queryKey: ['progress'] });
      }, 2000);
    },
  });

  // MCP tool execution mutation
  const executeMCPToolMutation = useMutation({
    mutationFn: ({ toolName, parameters }: { toolName: string; parameters: any }) => {
      return mcpApi.executeTool(toolName, parameters);
    },
    onSuccess: (result: any, { toolName }) => {
      toast.success(`MCP tool "${toolName}" executed successfully`);
      setMcpResult({ tool: toolName, data: result?.data ?? result });
      queryClient.invalidateQueries({ queryKey: ['progress'] });
    },
    onError: (err: any, { toolName }) => {
      toast.error(`MCP tool "${toolName}" failed`);
      setMcpResult({ tool: toolName, data: { error: err?.response?.data?.detail ?? err?.message ?? 'Unknown error' } });
    },
  });

  const summary = progressSummary?.data || {
    completed_lessons: 0,
    total_lessons: 0,
    current_streak: 0,
    total_time_spent: 0,
    average_score: 0,
    lessons_this_week: 0,
    skill_progress: {},
    weekly_breakdown: null as null | { day: string; lessons: number }[],
  };

  const weeklyData: { day: string; lessons: number }[] = summary.weekly_breakdown ?? [
    { day: 'Mon', lessons: 0 },
    { day: 'Tue', lessons: 0 },
    { day: 'Wed', lessons: 0 },
    { day: 'Thu', lessons: 0 },
    { day: 'Fri', lessons: 0 },
    { day: 'Sat', lessons: 0 },
    { day: 'Sun', lessons: 0 },
  ];

  const skillData = Object.entries(summary.skill_progress || {}).map(([skill, progress]) => ({
    skill,
    progress,
  }));

  const handleWorkflowTest = (workflowType: string, testData: any) => {
    triggerWorkflowMutation.mutate({ workflowType, data: testData });
  };

  const handleMCPTest = (toolName: string, parameters: any) => {
    executeMCPToolMutation.mutate({ toolName, parameters });
  };

  const completionRate = summary.total_lessons > 0
    ? (summary.completed_lessons / summary.total_lessons) * 100
    : 0;

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-black tracking-tight text-white uppercase flex items-center">
          <ChartBarIcon className="h-7 w-7 mr-3 text-orange-500" />
          Progress
        </h1>
        <p className="mt-1 text-sm text-zinc-500">
          Track your learning journey.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-zinc-900 border border-zinc-800 p-6">
          <div className="flex items-center">
            <TrophyIcon className="h-8 w-8 text-yellow-500" />
            <div className="ml-4">
              <p className="text-xs font-semibold text-zinc-500 uppercase tracking-widest">Completion Rate</p>
              <p className="text-3xl font-black text-white">{Math.round(completionRate)}%</p>
              <p className="text-xs text-zinc-600">{summary.completed_lessons} of {summary.total_lessons} lessons</p>
            </div>
          </div>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 p-6">
          <div className="flex items-center">
            <FireIcon className="h-8 w-8 text-orange-500" />
            <div className="ml-4">
              <p className="text-xs font-semibold text-zinc-500 uppercase tracking-widest">Current Streak</p>
              <p className="text-3xl font-black text-white">{summary.current_streak} days</p>
              <p className="text-xs text-zinc-600">Keep it up!</p>
            </div>
          </div>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 p-6">
          <div className="flex items-center">
            <ClockIcon className="h-8 w-8 text-green-500" />
            <div className="ml-4">
              <p className="text-xs font-semibold text-zinc-500 uppercase tracking-widest">Time Invested</p>
              <p className="text-3xl font-black text-white">{formatDate.duration(summary.total_time_spent)}</p>
              <p className="text-xs text-zinc-600">Total time learning</p>
            </div>
          </div>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 p-6">
          <div className="flex items-center">
            <BookOpenIcon className="h-8 w-8 text-purple-400" />
            <div className="ml-4">
              <p className="text-xs font-semibold text-zinc-500 uppercase tracking-widest">Average Score</p>
              <p className="text-3xl font-black text-white">{summary.average_score}%</p>
              <p className="text-xs text-zinc-600">Excellent work!</p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Weekly Activity Chart */}
        <div className="bg-zinc-900 border border-zinc-800 p-6">
          <h3 className="text-sm font-black uppercase tracking-widest text-white mb-4">Weekly Activity</h3>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={weeklyData} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
                <XAxis
                  dataKey="day"
                  tick={{ fill: '#71717a', fontSize: 11, fontWeight: 700 }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  allowDecimals={false}
                  tick={{ fill: '#71717a', fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip
                  cursor={{ fill: 'rgba(255,255,255,0.04)' }}
                  contentStyle={{ background: '#18181b', border: '1px solid #3f3f46', borderRadius: 0 }}
                  labelStyle={{ color: '#f4f4f5', fontWeight: 700, fontSize: 12, textTransform: 'uppercase' }}
                  itemStyle={{ color: '#f97316', fontSize: 12 }}
                  formatter={(value: number) => [value, 'Lessons']}
                />
                <Bar dataKey="lessons" fill="#f97316" radius={[2, 2, 0, 0]} maxBarSize={40} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Skill Progress Chart */}
        <div className="bg-zinc-900 border border-zinc-800 p-6">
          <h3 className="text-sm font-black uppercase tracking-widest text-white mb-4">Skill Progress</h3>
          <div className="space-y-4">
            {Object.entries(summary.skill_progress || {}).map(([skill, progress]) => (
              <div key={skill}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="font-semibold text-zinc-300">{skill}</span>
                  <span className="text-zinc-500 font-mono">{progress as number}%</span>
                </div>
                <div className="w-full bg-zinc-800 h-1.5">
                  <div 
                    className="bg-orange-500 h-1.5 transition-all duration-500"
                    style={{ width: `${progress as number}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* n8n Workflow Testing */}
      <div className="bg-orange-50 border border-orange-200 rounded-lg p-6 mb-8">
        <div className="flex items-center mb-4">
          <CogIcon className="h-6 w-6 text-orange-600 mr-3" />
          <h3 className="text-lg font-semibold text-orange-900">n8n Workflow Testing</h3>
        </div>
        
        <p className="text-sm text-orange-700 mb-4">
          Test automated workflows that trigger based on your learning progress and performance.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <button
            onClick={() => handleWorkflowTest('daily_practice_reminder', { user_id: user?.id })}
            disabled={workflowTesting['daily_practice_reminder']}
            className="flex items-center justify-center px-4 py-2 border border-orange-300 rounded-md text-sm font-medium text-orange-700 bg-zinc-900 hover:bg-orange-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {workflowTesting['daily_practice_reminder'] ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-orange-600 mr-2"></div>
            ) : (
              <CalendarIcon className="h-4 w-4 mr-2" />
            )}
            Daily Reminder
          </button>

          <button
            onClick={() => handleWorkflowTest('low_performance_intervention', { 
              user_id: user?.id, 
              score: 45,
              lesson_id: 'test-lesson'
            })}
            disabled={workflowTesting['low_performance_intervention']}
            className="flex items-center justify-center px-4 py-2 border border-orange-300 rounded-md text-sm font-medium text-orange-700 bg-zinc-900 hover:bg-orange-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {workflowTesting['low_performance_intervention'] ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-orange-600 mr-2"></div>
            ) : (
              <LightBulbIcon className="h-4 w-4 mr-2" />
            )}
            Low Performance
          </button>

          <button
            onClick={() => handleWorkflowTest('weekly_progress_summary', { user_id: user?.id })}
            disabled={workflowTesting['weekly_progress_summary']}
            className="flex items-center justify-center px-4 py-2 border border-orange-300 rounded-md text-sm font-medium text-orange-700 bg-zinc-900 hover:bg-orange-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {workflowTesting['weekly_progress_summary'] ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-orange-600 mr-2"></div>
            ) : (
              <ChartBarIcon className="h-4 w-4 mr-2" />
            )}
            Weekly Summary
          </button>

          <button
            onClick={() => handleWorkflowTest('lesson_completion_handler', {
              user_id: user?.id,
              lesson_id: 'test-completion',
              score: 95
            })}
            disabled={workflowTesting['lesson_completion_handler']}
            className="flex items-center justify-center px-4 py-2 border border-orange-300 rounded-md text-sm font-medium text-orange-700 bg-zinc-900 hover:bg-orange-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {workflowTesting['lesson_completion_handler'] ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-orange-600 mr-2"></div>
            ) : (
              <CheckCircleIcon className="h-4 w-4 mr-2" />
            )}
            Lesson Complete
          </button>
        </div>

        <div className="mt-4 p-3 bg-zinc-900 rounded border">
          <p className="text-xs font-medium text-orange-900 mb-2">Expected n8n Workflows:</p>
          <div className="text-xs text-orange-700 space-y-1">
            <div>• <strong>Daily Practice Reminder:</strong> Triggers scheduled notifications</div>
            <div>• <strong>Low Performance:</strong> Sends intervention recommendations</div>
            <div>• <strong>Weekly Summary:</strong> Generates progress reports</div>
            <div>• <strong>Lesson Complete:</strong> Unlocks next lessons & achievements</div>
          </div>
        </div>
      </div>

      {/* MCP Tool Testing */}
      <div className="bg-zinc-900 border border-zinc-800 border-l-4 border-l-purple-500 p-6">
        <div className="flex items-center mb-4">
          <CogIcon className="h-5 w-5 text-purple-400 mr-3" />
          <h3 className="text-sm font-black uppercase tracking-widest text-white">MCP Tool Testing</h3>
        </div>
        
        <p className="text-sm text-zinc-500 mb-4">
          Test Model Context Protocol tools for AI interaction with learning data.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <button
            onClick={() => handleMCPTest('get_user_progress', { user_id: user?.id })}
            className="flex items-center justify-center px-4 py-2 border border-zinc-700 text-sm font-semibold text-zinc-300 bg-zinc-800 hover:border-purple-500 hover:text-white transition-colors"
          >
            <ChartBarIcon className="h-4 w-4 mr-2" />
            Get Progress
          </button>

          <button
            onClick={() => handleMCPTest('fetch_recommendations', { 
              user_id: user?.id,
              skill_level: user?.skill_level || 'beginner'
            })}
            className="flex items-center justify-center px-4 py-2 border border-zinc-700 text-sm font-semibold text-zinc-300 bg-zinc-800 hover:border-purple-500 hover:text-white transition-colors"
          >
            <LightBulbIcon className="h-4 w-4 mr-2" />
            Get Recommendations
          </button>

          <button
            onClick={() => handleMCPTest('schedule_reminder', {
              user_id: user?.id,
              reminder_type: 'practice',
              title: 'Time to practice drawing!'
            })}
            className="flex items-center justify-center px-4 py-2 border border-zinc-700 text-sm font-semibold text-zinc-300 bg-zinc-800 hover:border-purple-500 hover:text-white transition-colors"
          >
            <CalendarIcon className="h-4 w-4 mr-2" />
            Schedule Reminder
          </button>
        </div>

        {/* Result panel */}
        {mcpResult && (
          <div className="mt-4 border border-zinc-700">
            <div className="flex items-center justify-between px-3 py-2 bg-zinc-800 border-b border-zinc-700">
              <span className="text-xs font-black uppercase tracking-widest text-purple-400">
                {mcpResult.tool} — result
              </span>
              <button
                onClick={() => setMcpResult(null)}
                className="text-xs text-zinc-500 hover:text-white transition-colors"
              >
                ✕ clear
              </button>
            </div>
            <div className="p-3 bg-zinc-950 overflow-auto max-h-72">
              {mcpResult.tool === 'get_user_progress' && !mcpResult.data?.error && (
                <div className="text-xs text-zinc-300 space-y-1">
                  <div className="grid grid-cols-2 gap-2">
                    <div className="bg-zinc-800 p-2"><span className="text-zinc-500">Completed</span><br/><span className="font-bold text-white">{mcpResult.data?.result?.completed_lessons ?? 0}</span></div>
                    <div className="bg-zinc-800 p-2"><span className="text-zinc-500">Avg Score</span><br/><span className="font-bold text-white">{mcpResult.data?.result?.average_score ?? 0}%</span></div>
                    <div className="bg-zinc-800 p-2"><span className="text-zinc-500">Skill Level</span><br/><span className="font-bold text-white capitalize">{mcpResult.data?.result?.skill_level ?? '—'}</span></div>
                    <div className="bg-zinc-800 p-2"><span className="text-zinc-500">Recent Activity</span><br/><span className="font-bold text-white">{mcpResult.data?.result?.recent_activity_days ?? 0} sessions</span></div>
                  </div>
                </div>
              )}
              {mcpResult.tool === 'fetch_recommendations' && !mcpResult.data?.error && (
                <div className="text-xs text-zinc-300 space-y-2">
                  {(mcpResult.data?.result?.recommendations ?? []).length === 0 && (
                    <p className="text-zinc-500">No recommendations available yet.</p>
                  )}
                  {(mcpResult.data?.result?.recommendations ?? []).map((r: any, i: number) => (
                    <div key={i} className="bg-zinc-800 p-2">
                      <div className="font-bold text-white">{r.title}</div>
                      <div className="text-zinc-500">{r.difficulty} · {r.lesson_type} · {r.duration_minutes} min</div>
                      <div className="text-purple-400 mt-1">{r.reason}</div>
                    </div>
                  ))}
                </div>
              )}
              {mcpResult.tool === 'schedule_reminder' && !mcpResult.data?.error && (
                <div className="text-xs text-zinc-300 space-y-1">
                  <div className="bg-zinc-800 p-2">
                    <div className="font-bold text-white">Reminder scheduled ✓</div>
                    <div className="text-zinc-500 mt-1">Scheduled for: {mcpResult.data?.result?.next_occurrence ? new Date(mcpResult.data.result.next_occurrence).toLocaleString() : '—'}</div>
                    <div className="text-zinc-500">Reminder ID: {mcpResult.data?.result?.reminder_id ?? '—'}</div>
                  </div>
                </div>
              )}
              {mcpResult.data?.error && (
                <div className="text-xs text-red-400 p-2 bg-red-950/30">{mcpResult.data.error}</div>
              )}
              {/* Raw JSON fallback for unexpected shapes */}
              {!['get_user_progress','fetch_recommendations','schedule_reminder'].includes(mcpResult.tool) && !mcpResult.data?.error && (
                <pre className="text-xs text-zinc-400 whitespace-pre-wrap break-all">{JSON.stringify(mcpResult.data?.result ?? mcpResult.data, null, 2)}</pre>
              )}
            </div>
          </div>
        )}

        <div className="mt-4 p-3 bg-zinc-800 border border-zinc-700">
          <p className="text-xs font-bold text-zinc-400 uppercase tracking-widest mb-2">Expected MCP Tools:</p>
          <div className="text-xs text-zinc-500 space-y-1">
            <div>• <strong className="text-zinc-400">get_user_progress:</strong> Retrieves learning progress data</div>
            <div>• <strong className="text-zinc-400">fetch_recommendations:</strong> Gets personalized lesson suggestions</div>
            <div>• <strong className="text-zinc-400">schedule_reminder:</strong> Creates automated practice reminders</div>
            <div>• <strong className="text-zinc-400">update_progress:</strong> Updates lesson completion status</div>
            <div>• <strong className="text-zinc-400">generate_lesson:</strong> Creates custom learning content</div>
            <div>• <strong className="text-zinc-400">evaluate_quiz:</strong> Processes quiz results and feedback</div>
          </div>
        </div>
      </div>
    </div>
  );
}






