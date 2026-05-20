import { useEffect, useState } from 'react';
import '../styles/ThemeToggle.css';

export default function ThemeToggle({ onThemeChange }) {
  const [isDark, setIsDark] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('theme') === 'dark';
    }
    return false;
  });

  useEffect(() => {
    const newTheme = isDark ? 'dark' : 'light';
    localStorage.setItem('theme', newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
    onThemeChange(newTheme);
  }, [isDark, onThemeChange]);

  return (
    <button
      className="theme-toggle"
      onClick={() => setIsDark(!isDark)}
      aria-label="Toggle dark mode"
      title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
    >
      <span className="toggle-icon">
        {isDark ? '☀️' : <span className="night-logo">N</span>}
      </span>
    </button>
  );
}
