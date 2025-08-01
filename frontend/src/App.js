import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate, Link } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import Onboarding from './components/Onboarding';
import { api_unauthenticated } from './services/api';

function App() {
  const [userCount, setUserCount] = useState(null);

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

  if (userCount === null) {
    return <div>Loading...</div>;
  }

  return (
    <Router>
      <nav>
        <Link to="/login">Login</Link> | <Link to="/register">Register</Link> | <Link to="/">Dashboard</Link>
      </nav>
      <Routes>
        {userCount === 0 && <Route path="/*" element={<Navigate to="/onboarding" />} />}
        <Route path="/onboarding" element={<Onboarding />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/" element={<Dashboard />} />
      </Routes>
    </Router>
  );
}

export default App;
