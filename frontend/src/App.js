import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate, Link } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import Onboarding from './components/Onboarding';
import api, { api_unauthenticated } from './services/api';
import './App.css';

function App() {
  const [userCount, setUserCount] = useState(null);
  const [user, setUser] = useState(null);

  const handleOnboardingSuccess = () => {
    setUserCount(1); // Optimistically update user count
  };

  useEffect(() => {
    const fetchUser = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const res = await api.get('/me/');
          setUser(res.data);
        } catch (err) {
          console.error(err);
        }
      }
    };
    fetchUser();
  }, []);

  useEffect(() => {
    const checkUserCount = async () => {
      try {
        const res = await api_unauthenticated.get('/user-count/');
        setUserCount(res.data.user_count);
      } catch (err) {
        console.error(err);
      }
    };
    checkUserCount();
  }, []);

  const AppRoutes = () => {
    if (userCount === null) {
      return <div>Loading...</div>;
    }

    if (userCount === 0) {
      return (
        <Routes>
          <Route path="/onboarding" element={<Onboarding onOnboardingSuccess={handleOnboardingSuccess} />} />
          <Route path="/*" element={<Navigate to="/onboarding" />} />
        </Routes>
      );
    }

    return (
        <>
          <nav>
            <Link to="/login">Login</Link> | <Link to="/register">Register</Link> | <Link to="/">Dashboard</Link>
          </nav>
          <div className="container">
            <Routes>
              <Route path="/onboarding" element={<Onboarding onOnboardingSuccess={handleOnboardingSuccess} />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/" element={<Dashboard user={user} />} />
            </Routes>
          </div>
        </>
    );
  };

  return (
    <Router>
      <AppRoutes />
    </Router>
  );
}

export default App;
