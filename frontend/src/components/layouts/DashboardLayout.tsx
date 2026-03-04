import { ReactNode, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/useAuthStore';
import { 
  HomeIcon, 
  BookOpenIcon, 
  ChartBarIcon, 
  UserCircleIcon,
  ChatBubbleLeftRightIcon,
  Bars3Icon,
  XMarkIcon,
  ArrowRightStartOnRectangleIcon
} from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';

interface DashboardLayoutProps {
  children: ReactNode;
}

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'Lessons', href: '/lessons', icon: BookOpenIcon },
  { name: 'Progress', href: '/progress', icon: ChartBarIcon },
  { name: 'AI Tutor', href: '/tutor', icon: ChatBubbleLeftRightIcon },
  { name: 'Profile', href: '/profile', icon: UserCircleIcon },
];

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { user, logout } = useAuthStore();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
      toast.success('Logged out successfully');
      navigate('/login');
    } catch (error) {
      toast.error('Error logging out');
    }
  };

  const NavLinks = ({ onClose }: { onClose?: () => void }) => (
    <ul role="list" className="-mx-2 space-y-0.5">
      {navigation.map((item) => {
        const isActive = location.pathname === item.href || location.pathname.startsWith(item.href + '/');
        return (
          <li key={item.name}>
            <Link
              to={item.href}
              onClick={onClose}
              className={`group flex gap-x-3 p-3 text-sm font-semibold tracking-wide uppercase border-l-2 transition-colors ${
                isActive
                  ? 'border-orange-500 bg-zinc-800 text-white'
                  : 'border-transparent text-zinc-400 hover:text-white hover:bg-zinc-800 hover:border-zinc-600'
              }`}
            >
              <item.icon
                className={`h-5 w-5 shrink-0 ${
                  isActive ? 'text-orange-500' : 'text-zinc-600 group-hover:text-zinc-300'
                }`}
                aria-hidden="true"
              />
              {item.name}
            </Link>
          </li>
        );
      })}
    </ul>
  );

  return (
    <div className="min-h-screen bg-zinc-950">
      {/* Mobile sidebar */}
      <div className={`relative z-50 lg:hidden ${sidebarOpen ? '' : 'hidden'}`}>
        <div className="fixed inset-0 bg-black/80" onClick={() => setSidebarOpen(false)} />
        <div className="fixed inset-0 flex">
          <div className="relative mr-16 flex w-full max-w-xs flex-1">
            <div className="absolute left-full top-0 flex w-16 justify-center pt-5">
              <button
                type="button"
                className="-m-2.5 p-2.5"
                onClick={() => setSidebarOpen(false)}
              >
                <span className="sr-only">Close sidebar</span>
                <XMarkIcon className="h-6 w-6 text-white" aria-hidden="true" />
              </button>
            </div>
            <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-zinc-950 border-r border-zinc-800 px-4 pb-2">
              <div className="flex h-16 shrink-0 items-center gap-3 px-2">
                <div className="bg-orange-500 p-1.5">
                  <svg className="h-5 w-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                </div>
                <span className="text-base font-black tracking-widest text-white uppercase">Art Buddy</span>
              </div>
              <nav className="flex flex-1 flex-col">
                <ul role="list" className="flex flex-1 flex-col gap-y-7">
                  <li><NavLinks onClose={() => setSidebarOpen(false)} /></li>
                </ul>
              </nav>
            </div>
          </div>
        </div>
      </div>

      {/* Static sidebar for desktop */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-64 lg:flex-col">
        <div className="flex grow flex-col gap-y-5 overflow-y-auto border-r border-zinc-800 bg-zinc-950 px-4">
          <div className="flex h-16 shrink-0 items-center gap-3 px-2">
            <div className="bg-orange-500 p-1.5">
              <svg className="h-5 w-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <span className="text-base font-black tracking-widest text-white uppercase">Art Buddy</span>
          </div>
          <nav className="flex flex-1 flex-col">
            <ul role="list" className="flex flex-1 flex-col gap-y-7">
              <li><NavLinks /></li>
              {/* User section */}
              <li className="-mx-4 mt-auto border-t border-zinc-800">
                <div className="flex items-center gap-x-3 px-4 py-4 text-sm font-semibold text-zinc-400">
                  <div className="h-8 w-8 bg-orange-500 flex items-center justify-center flex-shrink-0">
                    <span className="text-white text-sm font-bold">
                      {user?.name?.charAt(0)?.toUpperCase() || 'U'}
                    </span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-white truncate">{user?.name || 'User'}</div>
                    <div className="text-xs text-zinc-600 truncate">{user?.email}</div>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="text-zinc-600 hover:text-orange-500 transition-colors"
                    title="Logout"
                  >
                    <ArrowRightStartOnRectangleIcon className="h-5 w-5" />
                  </button>
                </div>
              </li>
            </ul>
          </nav>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Sticky top header */}
        <div className="sticky top-0 z-40 flex h-14 shrink-0 items-center gap-x-4 border-b border-zinc-800 bg-zinc-950 px-4 sm:gap-x-6 sm:px-6 lg:px-8">
          <button
            type="button"
            className="-m-2.5 p-2.5 text-zinc-500 lg:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <span className="sr-only">Open sidebar</span>
            <Bars3Icon className="h-6 w-6" aria-hidden="true" />
          </button>
          <div className="h-5 w-px bg-zinc-800 lg:hidden" aria-hidden="true" />
          <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
            <div className="flex flex-1 items-center" />
            <div className="flex items-center gap-x-4 lg:hidden">
              <div className="flex items-center gap-x-2">
                <div className="h-7 w-7 bg-orange-500 flex items-center justify-center">
                  <span className="text-white text-xs font-bold">
                    {user?.name?.charAt(0)?.toUpperCase() || 'U'}
                  </span>
                </div>
                <button
                  onClick={handleLogout}
                  className="text-zinc-600 hover:text-orange-500 transition-colors"
                  title="Logout"
                >
                  <ArrowRightStartOnRectangleIcon className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="py-6">
          {children}
        </main>
      </div>
    </div>
  );
}
