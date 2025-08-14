import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate, Link } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import Onboarding from './components/Onboarding';
import api, { api_unauthenticated } from './services/api';
import './App.css';

const AppRoutes = ({ userCount, user, onOnboardingSuccess, onLogin }) => {
  console.log('AppRoutes render, userCount:', userCount);
  if (userCount === null) {
    return <div>Loading...</div>;
  }

  if (userCount === 0) {
    return (
      <Routes>
        <Route path="/onboarding" element={<Onboarding onOnboardingSuccess={onOnboardingSuccess} />} />
        <Route path="/*" element={<Navigate to="/onboarding" />} />
      </Routes>
    );
  }

  return (
      <>
        <nav>
          <Link to="/login">Login</Link> | <Link to="/register">Register</Link> | <Link to="/dashboard">Dashboard</Link>
        </nav>
        <div className="container">
          <Routes>
            <Route path="/onboarding" element={<Onboarding onOnboardingSuccess={onOnboardingSuccess} />} />
            <Route path="/login" element={<Login onLogin={onLogin} />} />
            <Route path="/register" element={<Register />} />
            <Route path="/dashboard" element={<Dashboard user={user} />} />
            <Route path="/" element={<Navigate to="/dashboard" />} />
          </Routes>
        </div>
      </>
  );
};

function App() {
  console.log('App render');
  const [userCount, setUserCount] = useState(null);
  const [user, setUser] = useState(null);

  const handleOnboardingSuccess = () => {
    console.log('handleOnboardingSuccess');
    setUserCount(1);
  };

  useEffect(() => {
    console.log('useEffect fetchUser');
    const fetchUser = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const res = await api.get('/me/');
          console.log('fetchUser success', res.data);
          setUser(res.data);
        } catch (err) {
          console.error('fetchUser error', err);
        }
      } else {
        console.log('fetchUser no token');
      }
    };
    fetchUser();
  }, []);

  useEffect(() => {
    console.log('useEffect checkUserCount');
    const checkUserCount = async () => {
      try {
        const res = await api_unauthenticated.get('/user-count/');
        console.log('checkUserCount success', res.data);
        setUserCount(res.data.user_count);
      } catch (err) {
        console.error('checkUserCount error', err);
      }
    };
    checkUserCount();
  }, []);

  return (
    <Router>
      <AppRoutes
        userCount={userCount}
        user={user}
        onOnboardingSuccess={handleOnboardingSuccess}
        onLogin={setUser}
      />
    </Router>
  );
}

export default App;
