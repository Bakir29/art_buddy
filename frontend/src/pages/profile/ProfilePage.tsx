import { useState, useEffect } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useAuthStore } from '@/stores/useAuthStore';
import { useThemeStore } from '@/stores/useThemeStore';
import { usersApi, aiApi } from '@/services/api';
import {
  UserIcon,
  CogIcon,
  BellIcon,
  PaintBrushIcon,
  AcademicCapIcon,
  PencilIcon,
  CheckIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';

interface UserProfile {
  id: string;
  name: string;
  email: string;
  skill_level: 'beginner' | 'intermediate' | 'advanced';
  art_interests: string[];
  notification_preferences: {
    daily_reminders: boolean;
    progress_updates: boolean;
    new_lessons: boolean;
    achievement_notifications: boolean;
  };
  profile_picture?: string;
  bio?: string;
  learning_goals: string[];
}

export function ProfilePage() {
  const { user } = useAuthStore();
  const { isDark, toggleTheme } = useThemeStore();
  const queryClient = useQueryClient();
  const [isEditing, setIsEditing] = useState(false);
  const [activeTab, setActiveTab] = useState('profile');
  const [editedProfile, setEditedProfile] = useState<Partial<UserProfile>>({});

  // Fetch full user profile
  const { data: profile, isLoading } = useQuery({
    queryKey: ['user', 'profile', user?.id],
    queryFn: () => usersApi.getProfile(),
    enabled: !!user?.id,
    refetchOnWindowFocus: false,
    staleTime: 5 * 60 * 1000,  // cache for 5 minutes — repeat visits are instant
    gcTime: 10 * 60 * 1000,
  });

  // Update profile mutation
  const updateProfileMutation = useMutation({
    mutationFn: (profileData: Partial<UserProfile>) => 
      usersApi.updateProfile(profileData),
    onSuccess: () => {
      setIsEditing(false);
      setEditedProfile({});
      queryClient.invalidateQueries({ queryKey: ['user', 'profile'] });
    },
  });

  // Generate AI learning recommendations mutation
  const generateRecommendationsMutation = useMutation({
    mutationFn: () => aiApi.askQuestion({
      user_id: user?.id || '',
      question: 'Generate personalized learning recommendations based on my skill level and interests',
      context: `skill_level:${user?.skill_level},interests:${currentProfile.art_interests.join(',')}`
    }),
  });

  useEffect(() => {
    if (profile?.data && !editedProfile.name) {
      setEditedProfile(profile.data);
    }
  }, [profile]);

  const currentProfile = profile?.data || {
    id: user?.id || '',
    name: user?.name || '',
    email: user?.email || '',
    skill_level: user?.skill_level || 'beginner',
    art_interests: ['Drawing', 'Digital Art'],
    notification_preferences: {
      daily_reminders: true,
      progress_updates: true,
      new_lessons: true,
      achievement_notifications: true,
    },
    bio: 'Art enthusiast learning through AI-guided instruction.',
    learning_goals: ['Master color theory', 'Improve drawing fundamentals', 'Learn digital art techniques'],
  };

  const handleProfileUpdate = () => {
    updateProfileMutation.mutate(editedProfile);
  };

  const handleCancel = () => {
    setEditedProfile(currentProfile);
    setIsEditing(false);
  };

  const artInterestOptions = [
    'Drawing', 'Painting', 'Digital Art', 'Watercolor', 'Oil Painting', 
    'Sketching', 'Character Design', 'Landscape Art', 'Portrait Art', 
    'Abstract Art', 'Comics', 'Animation', 'Sculpture', 'Mixed Media'
  ];

  const skillLevelDescriptions = {
    beginner: 'New to art, learning basic concepts and techniques',
    intermediate: 'Some experience, ready for more advanced techniques',
    advanced: 'Experienced artist looking to refine and master skills'
  };

  // Only show skeleton if we have no data at all (auth store always has user, so this is essentially never)
  if (isLoading && !user) {
    return (
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="animate-pulse">
          <div className="h-8 bg-zinc-800 w-1/4 mb-4"></div>
          <div className="bg-zinc-900 border border-zinc-800 p-6">
            <div className="h-20 bg-zinc-800 mb-4"></div>
            <div className="space-y-3">
              <div className="h-4 bg-zinc-800 w-3/4"></div>
              <div className="h-4 bg-zinc-800 w-1/2"></div>
              <div className="h-4 bg-zinc-800 w-2/3"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-2xl font-black uppercase text-zinc-100 flex items-center">
          <UserIcon className="h-7 w-7 mr-3 text-orange-500" />
          My Profile
        </h1>
        <p className="mt-1 text-sm text-zinc-400 uppercase tracking-widest">
          Manage your account settings and learning preferences.
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-zinc-800 mb-6">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'profile', name: 'Profile', icon: UserIcon },
            { id: 'preferences', name: 'Preferences', icon: CogIcon },
            { id: 'notifications', name: 'Notifications', icon: BellIcon },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`${
                activeTab === tab.id
                  ? 'border-orange-500 text-orange-500'
                  : 'border-transparent text-zinc-500 hover:text-zinc-300 hover:border-zinc-600'
              } whitespace-nowrap py-2 px-1 border-b-2 font-bold text-sm uppercase tracking-widest flex items-center`}
            >
              <tab.icon className="h-4 w-4 mr-2" />
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Profile Tab */}
      {activeTab === 'profile' && (
        <div className="bg-zinc-900 border border-zinc-800">
          {/* Profile Header */}
          <div className="px-6 py-4 border-b border-zinc-800">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="h-16 w-16 bg-gradient-to-br from-orange-500 to-orange-700 flex items-center justify-center">
                  <span className="text-2xl font-black text-black">
                    {currentProfile.name.charAt(0).toUpperCase()}
                  </span>
                </div>
                <div className="ml-4">
                  <h2 className="text-xl font-black uppercase text-zinc-100">{currentProfile.name}</h2>
                  <p className="text-sm text-zinc-500">{currentProfile.email}</p>
                  <div className="flex items-center mt-1">
                    <AcademicCapIcon className="h-4 w-4 text-zinc-500 mr-1" />
                    <span className="text-sm text-zinc-400 capitalize">{currentProfile.skill_level}</span>
                  </div>
                </div>
              </div>
              <button
                onClick={() => setIsEditing(!isEditing)}
                className="flex items-center px-3 py-2 border border-zinc-700 text-sm font-bold uppercase tracking-widest text-zinc-300 hover:bg-zinc-800 hover:border-zinc-500 transition-colors"
              >
                {isEditing ? (
                  <>
                    <XMarkIcon className="h-4 w-4 mr-2" />
                    Cancel
                  </>
                ) : (
                  <>
                    <PencilIcon className="h-4 w-4 mr-2" />
                    Edit Profile
                  </>
                )}
              </button>
            </div>
          </div>

          <div className="p-6">
            {/* Bio Section */}
            <div className="mb-6">
              <label className="block text-sm font-bold uppercase tracking-widest text-zinc-400 mb-2">Bio</label>
              {isEditing ? (
                <textarea
                  value={editedProfile.bio || ''}
                  onChange={(e) => setEditedProfile(prev => ({ ...prev, bio: e.target.value }))}
                  rows={3}
                  className="w-full bg-zinc-800 border border-zinc-700 px-3 py-2 text-zinc-200 placeholder-zinc-600 focus:outline-none focus:border-orange-500"
                  placeholder="Tell us about your art journey..."
                />
              ) : (
                <p className="text-zinc-300">{currentProfile.bio}</p>
              )}
            </div>

            {/* Skill Level */}
            <div className="mb-6">
              <label className="block text-sm font-bold uppercase tracking-widest text-zinc-400 mb-2">Skill Level</label>
              {isEditing ? (
                <select
                  value={editedProfile.skill_level || currentProfile.skill_level}
                  onChange={(e) => setEditedProfile(prev => ({ 
                    ...prev, 
                    skill_level: e.target.value as 'beginner' | 'intermediate' | 'advanced'
                  }))}
                  className="w-full bg-zinc-800 border border-zinc-700 px-3 py-2 text-zinc-200 focus:outline-none focus:border-orange-500"
                >
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              ) : (
                <div>
                  <p className="text-zinc-200 capitalize font-bold">{currentProfile.skill_level}</p>
                  <p className="text-sm text-zinc-500">{skillLevelDescriptions[currentProfile.skill_level as keyof typeof skillLevelDescriptions]}</p>
                </div>
              )}
            </div>

            {/* Art Interests */}
            <div className="mb-6">
              <label className="block text-sm font-bold uppercase tracking-widest text-zinc-400 mb-2">Art Interests</label>
              {isEditing ? (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {artInterestOptions.map((interest: string) => (
                    <label key={interest} className="inline-flex items-center">
                      <input
                        type="checkbox"
                        checked={editedProfile.art_interests?.includes(interest) || currentProfile.art_interests.includes(interest)}
                        onChange={(e) => {
                          const currentInterests = editedProfile.art_interests || currentProfile.art_interests;
                          if (e.target.checked) {
                            setEditedProfile(prev => ({
                              ...prev,
                              art_interests: [...currentInterests, interest]
                            }));
                          } else {
                            setEditedProfile(prev => ({
                              ...prev,
                              art_interests: currentInterests.filter(i => i !== interest)
                            }));
                          }
                        }}
                        className="border-zinc-600 bg-zinc-800 text-orange-500 focus:ring-orange-500"
                      />
                      <span className="ml-2 text-sm text-zinc-300">{interest}</span>
                    </label>
                  ))}
                </div>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {currentProfile.art_interests.map((interest: string) => (
                    <span
                      key={interest}
                      className="inline-flex items-center px-2.5 py-0.5 border border-zinc-700 text-xs font-bold uppercase tracking-widest text-zinc-300"
                    >
                      <PaintBrushIcon className="h-3 w-3 mr-1 text-orange-500" />
                      {interest}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Learning Goals */}
            <div className="mb-6">
              <label className="block text-sm font-bold uppercase tracking-widest text-zinc-400 mb-2">Learning Goals</label>
              {isEditing ? (
                <div className="space-y-2">
                  {(editedProfile.learning_goals || currentProfile.learning_goals).map((goal: string, index: number) => (
                    <div key={index} className="flex items-center">
                      <input
                        type="text"
                        value={goal}
                        onChange={(e) => {
                          const newGoals = [...(editedProfile.learning_goals || currentProfile.learning_goals)];
                          newGoals[index] = e.target.value;
                          setEditedProfile(prev => ({ ...prev, learning_goals: newGoals }));
                        }}
                        className="flex-1 bg-zinc-800 border border-zinc-700 px-3 py-2 text-zinc-200 focus:outline-none focus:border-orange-500"
                      />
                      <button
                        onClick={() => {
                          const newGoals = (editedProfile.learning_goals || currentProfile.learning_goals).filter((_: string, i: number) => i !== index);
                          setEditedProfile(prev => ({ ...prev, learning_goals: newGoals }));
                        }}
                        className="ml-2 text-red-500 hover:text-red-400"
                      >
                        <XMarkIcon className="h-4 w-4" />
                      </button>
                    </div>
                  ))}
                  <button
                    onClick={() => {
                      const newGoals = [...(editedProfile.learning_goals || currentProfile.learning_goals), ''];
                      setEditedProfile(prev => ({ ...prev, learning_goals: newGoals }));
                    }}
                    className="text-orange-500 hover:text-orange-400 text-sm font-bold uppercase tracking-widest"
                  >
                    + Add Goal
                  </button>
                </div>
              ) : (
                <ul className="space-y-1">
                  {currentProfile.learning_goals.map((goal: string, index: number) => (
                    <li key={index} className="flex items-center text-zinc-300">
                      <CheckIcon className="h-4 w-4 text-orange-500 mr-2 flex-shrink-0" />
                      {goal}
                    </li>
                  ))}
                </ul>
              )}
            </div>

            {/* Action Buttons */}
            {isEditing && (
              <div className="flex justify-end space-x-3 pt-4 border-t border-zinc-800">
                <button
                  onClick={handleCancel}
                  className="px-4 py-2 border border-zinc-700 text-sm font-bold uppercase tracking-widest text-zinc-300 hover:bg-zinc-800 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleProfileUpdate}
                  disabled={updateProfileMutation.isPending}
                  className="px-4 py-2 bg-orange-500 text-black text-sm font-black uppercase tracking-widest hover:bg-orange-400 disabled:opacity-50 transition-colors flex items-center"
                >
                  {updateProfileMutation.isPending ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-black mr-2"></div>
                  ) : (
                    <CheckIcon className="h-4 w-4 mr-2" />
                  )}
                  Save Changes
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Preferences Tab */}
      {activeTab === 'preferences' && (
        <div className="bg-zinc-900 border border-zinc-800 p-6">
          <h3 className="text-lg font-black uppercase text-zinc-100 mb-4">Learning Preferences</h3>
          
          <div className="space-y-6">
            <div className="flex items-center justify-between py-3 border-b border-zinc-800">
              <div>
                <h4 className="text-sm font-bold uppercase tracking-widest text-zinc-200">AI Personalization</h4>
                <p className="text-sm text-zinc-500">Get personalized lesson recommendations based on your progress</p>
              </div>
              <button
                onClick={() => generateRecommendationsMutation.mutate()}
                disabled={generateRecommendationsMutation.isPending}
                className="px-3 py-1 bg-orange-500 text-black font-bold uppercase tracking-widest text-sm hover:bg-orange-400 disabled:opacity-50 transition-colors"
              >
                {generateRecommendationsMutation.isPending ? 'Generating...' : 'Generate Now'}
              </button>
            </div>

            <div className="flex items-center justify-between py-3 border-b border-zinc-800">
              <div>
                <h4 className="text-sm font-bold uppercase tracking-widest text-zinc-200">Dark Mode</h4>
                <p className="text-sm text-zinc-500">Already enabled — you're living in it.</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" checked={isDark} onChange={toggleTheme} className="sr-only peer" />
                <div className="w-11 h-6 bg-zinc-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-orange-500"></div>
              </label>
            </div>

            <div className="flex items-center justify-between py-3">
              <div>
                <h4 className="text-sm font-bold uppercase tracking-widest text-zinc-200">Auto-save Progress</h4>
                <p className="text-sm text-zinc-500">Automatically save your lesson progress every few minutes</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" defaultChecked className="sr-only peer" />
                <div className="w-11 h-6 bg-zinc-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-orange-500"></div>
              </label>
            </div>
          </div>
        </div>
      )}

      {/* Notifications Tab */}
      {activeTab === 'notifications' && (
        <div className="bg-zinc-900 border border-zinc-800 p-6">
          <h3 className="text-lg font-black uppercase text-zinc-100 mb-4">Notification Preferences</h3>
          
          <div className="space-y-4">
            {Object.entries(currentProfile.notification_preferences).map(([key, enabled]) => {
              const labels = {
                daily_reminders: { title: 'Daily Practice Reminders', desc: 'Get reminded to practice art daily' },
                progress_updates: { title: 'Progress Updates', desc: 'Weekly summaries of your learning progress' },
                new_lessons: { title: 'New Lesson Alerts', desc: 'Notifications when new lessons are available' },
                achievement_notifications: { title: 'Achievement Badges', desc: 'Celebrate your learning milestones' }
              };
              
              return (
                <div key={key} className="flex items-center justify-between py-3 border-b border-zinc-800 last:border-b-0">
                  <div>
                    <h4 className="text-sm font-bold uppercase tracking-widest text-zinc-200">{labels[key as keyof typeof labels].title}</h4>
                    <p className="text-sm text-zinc-500">{labels[key as keyof typeof labels].desc}</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" defaultChecked={Boolean(enabled)} className="sr-only peer" />
                    <div className="w-11 h-6 bg-zinc-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-orange-500"></div>
                  </label>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* AI Recommendations */}
      {generateRecommendationsMutation.data && (
        <div className="mt-6 bg-zinc-900 border border-orange-500/40 p-6">
          <h3 className="text-lg font-black uppercase text-zinc-100 mb-3 flex items-center">
            <AcademicCapIcon className="h-5 w-5 mr-2 text-orange-500" />
            AI-Generated Recommendations
          </h3>
          <div className="text-sm text-zinc-300 whitespace-pre-wrap">
            {generateRecommendationsMutation.data.answer}
          </div>
        </div>
      )}
    </div>
  );
}






