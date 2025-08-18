import React, { useState, useEffect, useCallback, memo } from 'react';
import { Routes, Route, Navigate, Link, useNavigate } from 'react-router-dom';
import Login from './components/Login.jsx';
import Register from './components/Register.jsx';
import Dashboard from './components/Dashboard.jsx';
import Onboarding from './components/Onboarding.jsx';
import Documents from './components/Documents.jsx';
import api from './services/api';
import './App.css';

const AppRoutes = memo(({ user, onOnboardingSuccess, onLoginSuccess, handleLogout }) => {
  if (user === undefined) {
    return <div>Loading...</div>;
  }

  return (
    <>
      <nav>
        {user ? (
          <>
            <Link to="/dashboard">Dashboard</Link> | <Link to="/documents">Documents</Link> | <button onClick={handleLogout}>Logout</button>
          </>
        ) : (
          <>
            <Link to="/login">Login</Link> | <Link to="/register">Register</Link>
          </>
        )}
      </nav>
      <div className="container">
        <Routes>
          {user ? (
            <>
              <Route path="/dashboard" element={<Dashboard user={user} />} />
              <Route path="/documents" element={<Documents />} />
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
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const navigate = useNavigate();

  const handleLoginSuccess = useCallback(() => {
    setIsLoggedIn(true);
  }, []);

  const handleLogout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    setIsLoggedIn(false);
    navigate('/login');
  }, [navigate]);

  const handleOnboardingSuccess = useCallback(() => {
    setIsLoggedIn(true);
  }, []);

  useEffect(() => {
    const fetchUser = async () => {
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
    };
    fetchUser();
  }, [isLoggedIn]);

  return (
    <AppRoutes
      user={user}
      onOnboardingSuccess={handleOnboardingSuccess}
      onLoginSuccess={handleLoginSuccess}
      handleLogout={handleLogout}
    />
  );
}

export default App;
