import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ConnectionStatus from './ConnectionStatus';
import { auth } from '../firebaseConfig';
import { signInWithEmailAndPassword } from 'firebase/auth';

const version = process.env.APP_VERSION;

const Login = ({ onLoginSuccess }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const navigate = useNavigate();

  const { email, password } = formData;

  const onChange = (e) =>
    setFormData({ ...formData, [e.target.name]: e.target.value });

  const onSubmit = async (e) => {
    e.preventDefault();
    try {
      await signInWithEmailAndPassword(auth, email, password);
      onLoginSuccess();
      navigate('/dashboard');
    } catch (err) {
      console.error(err);
      // Handle login error
      alert(`Login Failed: ${err.code || 'Unknown Error'} - ${err.message}\n\nPlease check the /debug page to verify your configuration.`);
    }
  };

  return (
    <div>
      <h1>Login</h1>
      <ConnectionStatus />
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
        <button type="submit">Login</button>
      </form>
      <p>Version: {version}</p>
    </div>
  );
};

export default Login;
