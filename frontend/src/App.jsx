import { useState, useEffect } from 'react';
import Home from './pages/Home';
import ThemeToggle from './components/ThemeToggle';
import './styles/App.css';

function App() {
  const [theme, setTheme] = useState('light');

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
    document.documentElement.setAttribute('data-theme', savedTheme);
  }, []);

  const handleThemeChange = (newTheme) => {
    setTheme(newTheme);
  };

  return (
    <div className="app">
      <ThemeToggle onThemeChange={handleThemeChange} />
      <Home />
    </div>
  );
}

export default App;
