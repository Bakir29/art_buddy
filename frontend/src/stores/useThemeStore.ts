import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface ThemeState {
  isDark: boolean;
  toggleTheme: () => void;
  setDark: (dark: boolean) => void;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      isDark: true, // dark by default
      toggleTheme: () =>
        set((state) => {
          const next = !state.isDark;
          document.documentElement.classList.toggle('dark', next);
          return { isDark: next };
        }),
      setDark: (dark: boolean) => {
        document.documentElement.classList.toggle('dark', dark);
        set({ isDark: dark });
      },
    }),
    {
      name: 'art-buddy-theme',
    }
  )
);
