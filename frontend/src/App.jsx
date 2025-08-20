import React, { useState, useEffect, useCallback, memo, useRef } from 'react';
import { Routes, Route, Navigate, Link, useNavigate } from 'react-router-dom';
import Login from './components/Login.jsx';
import Register from './components/Register.jsx';
import Dashboard from './components/Dashboard.jsx';
import Onboarding from './components/Onboarding.jsx';
import Documents from './components/Documents.jsx';
import Profile from './components/Profile.jsx';
import Settings from './components/Settings.jsx';
import Admin from './components/Admin.jsx';
import UserProfileIcon from './components/UserProfileIcon.jsx';
import api from './services/api';
import './App.css';

const AppRoutes = memo(({ user, onOnboardingSuccess, onLoginSuccess, handleLogout }) => {
  const [isDropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  if (user === undefined) {
    return <div>Loading...</div>;
  }

  const registerButtonStyle = {
    backgroundColor: 'var(--accent-orange)',
    color: 'white',
    padding: '10px 15px',
    textDecoration: 'none',
    borderRadius: '5px',
  };

  return (
    <>
      <nav>
        {user ? (
          <>
            <Link to="/dashboard">Dashboard</Link>
            {user.role === 'admin' && <Link to="/admin">Admin</Link>}
            <div style={{ position: 'relative', marginLeft: 'auto' }} ref={dropdownRef}>
              <button onClick={() => setDropdownOpen(!isDropdownOpen)} style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
                <UserProfileIcon />
              </button>
              {isDropdownOpen && (
                <div style={{ position: 'absolute', right: 0, backgroundColor: 'white', border: '1px solid var(--neutral-gray)', borderRadius: '5px', zIndex: 10 }}>
                  <Link to="/profile" style={{ display: 'block', padding: '10px', textDecoration: 'none', color: 'var(--neutral-gray)' }}>Profile</Link>
                  <Link to="/settings" style={{ display: 'block', padding: '10px', textDecoration: 'none', color: 'var(--neutral-gray)' }}>Settings</Link>
                  <Link to="/documents" style={{ display: 'block', padding: '10px', textDecoration: 'none', color: 'var(--neutral-gray)' }}>Documents</Link>
                  <button onClick={() => { handleLogout(); setDropdownOpen(false); }} style={{ display: 'block', width: '100%', padding: '10px', background: 'none', border: 'none', textAlign: 'left', cursor: 'pointer', color: 'var(--neutral-gray)' }}>Logout</button>
                </div>
              )}
            </div>
          </>
        ) : (
          <>
            <Link to="/login">Login</Link>
            <Link to="/register" style={registerButtonStyle}>Register</Link>
          </>
        )}
      </nav>
      <div className="container">
        <Routes>
          {user ? (
            <>
              <Route path="/dashboard" element={<Dashboard user={user} />} />
              <Route path="/admin" element={<Admin />} />
              <Route path="/documents" element={<Documents />} />
              <Route path="/profile" element={<Profile />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/*" element={<Navigate to="/dashboard" />} />
            </>
          ) : (
            <>
              <Route path="/onboarding" element={<Onboarding onOnboardingSuccess={onOnboardingSuccess} onLoginSuccess={onLoginSuccess} />} />
              <Route path="/login" element={<Login onLoginSuccess={onLoginSuccess} />} />
              <Route path="/register" element={<Register />} />
              <Route path="/*" element={<Navigate to="/login" />} />
            </>
          )}
        </Routes>
      </div>
    </>
  );
});

function App() {
  const [user, setUser] = useState(undefined);
  const navigate = useNavigate();

  const fetchUser = useCallback(async () => {
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        const res = await api.get('/me/');
        setUser(res.data);
      } catch (err) {
        setUser(null);
      }
    } else {
      setUser(null);
    }
  }, []);

  const handleLogout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    navigate('/login');
  }, [navigate]);

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  return (
    <AppRoutes
      user={user}
      onOnboardingSuccess={fetchUser}
      onLoginSuccess={fetchUser}
      handleLogout={handleLogout}
    />
  );
}

export default App;
