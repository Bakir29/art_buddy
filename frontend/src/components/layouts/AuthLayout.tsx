import { ReactNode } from 'react';

interface AuthLayoutProps {
  children: ReactNode;
}

export function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-zinc-950 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Logo and Header */}
        <div className="text-center">
          <div className="flex justify-center">
            <div className="bg-orange-500 p-3">
              <svg
                className="h-8 w-8 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                />
              </svg>
            </div>
          </div>
          <h2 className="mt-6 text-4xl font-black tracking-tight text-white uppercase">
            Art Buddy
          </h2>
          <p className="mt-2 text-sm text-zinc-500 tracking-widest uppercase">
            AI-powered art learning
          </p>
        </div>

        {/* Auth Form Container */}
        <div className="bg-zinc-900 border border-zinc-800 py-8 px-4 sm:px-10">
          {children}
        </div>

        {/* Footer */}
        <div className="text-center text-xs text-zinc-700">
          <p>© 2025 Art Buddy. All rights reserved.</p>
        </div>
      </div>
    </div>
  );
}






