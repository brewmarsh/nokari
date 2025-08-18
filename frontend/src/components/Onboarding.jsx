import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api_unauthenticated } from '../services/api';

const Onboarding = ({ onOnboardingSuccess, onLoginSuccess }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    password2: '',
  });
  const navigate = useNavigate();

  const { email, password, password2 } = formData;

  const onChange = (e) =>
    setFormData({ ...formData, [e.target.name]: e.target.value });

  const onSubmit = async (e) => {
    e.preventDefault();
    if (password !== password2) {
      alert('Passwords do not match');
    } else {
      try {
        await api_unauthenticated.post('/register/', {
          email,
          password,
          is_superuser: true,
        });
        try {
          const res = await api_unauthenticated.post('/login/', { email, password });
          localStorage.setItem('access_token', res.data.access);
          localStorage.setItem('refresh_token', res.data.refresh);
          onOnboardingSuccess();
          onLoginSuccess();
          navigate('/');
        } catch (loginErr) {
            if (loginErr.response) {
                alert('Login after registration failed: ' + JSON.stringify(loginErr.response.data));
            } else if (loginErr.request) {
                alert('Login after registration failed: No response from server.');
            } else {
                alert('Login after registration failed: ' + loginErr.message);
            }
        }
      } catch (err) {
        if (err.response) {
          alert('Onboarding failed: ' + JSON.stringify(err.response.data));
        } else if (err.request) {
          alert('Onboarding failed: No response from server.');
        } else {
          alert('Onboarding failed: ' + err.message);
        }
      }
    }
  };

  return (
    <div>
      <h1>Welcome! Create a Superuser Account</h1>
      <form onSubmit={onSubmit}>
        <div>
          <input
            type="email"
            placeholder="Email"
            name="email"
            value={email}
            onChange={onChange}
            required
          />
        </div>
        <div>
          <input
            type="password"
            placeholder="Password"
            name="password"
            value={password}
            onChange={onChange}
            required
          />
        </div>
        <div>
          <input
            type="password"
            placeholder="Confirm Password"
            name="password2"
            value={password2}
            onChange={onChange}
            required
          />
        </div>
        <button type="submit">Create Superuser</button>
      </form>
    </div>
  );
};

export default Onboarding;
