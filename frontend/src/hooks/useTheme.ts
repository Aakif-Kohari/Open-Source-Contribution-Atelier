import { useContext } from "react";
import {useState, useEffect } from 'react';
import { ThemeContext, type ThemeContextValue, type Theme } from "./ThemeContext";

const THEME_KEY = 'app-theme';

export { ThemeProvider } from "./ThemeContext";
export type { ThemeContextValue } from "./ThemeContext";

export function useTheme(): ThemeContextValue {
  const [theme, setThemeState] = useState<Theme>(() => {
    // Load from localStorage on init
    const saved = localStorage.getItem(THEME_KEY);
    if (saved === 'dark' || saved === 'light' || saved === 'system') return saved as Theme;
    // Default based on system preference
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  });

  useEffect(() => {
    // Determine actual applied theme (resolve 'system') and apply to document
    const applied = theme === 'system'
      ? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
      : theme;
    document.documentElement.className = applied;
    // Save to localStorage
    localStorage.setItem(THEME_KEY, theme);
  }, [theme]);

  const setTheme: ThemeContextValue['setTheme'] = (t: Theme) => {
    setThemeState(t);
  };

  const toggleTheme = () => {
    setThemeState(prev => (prev === 'light' ? 'dark' : 'light'));
  };

  return { theme, setTheme, toggleTheme };
}