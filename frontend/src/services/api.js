import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers['Authorization'] = 'Bearer ' + token;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const api_unauthenticated = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    console.log('API response error interceptor triggered.');

    if (error.response) {
      console.log('Error status:', error.response.status);
      if (error.response.status === 401 && !originalRequest._retry) {
        console.log('Attempting to refresh token.');
        originalRequest._retry = true;
        const refreshToken = localStorage.getItem('refresh_token');

        if (refreshToken) {
          console.log('Found refresh token.');
          try {
            const res = await api_unauthenticated.post('/login/refresh/', {
              refresh: refreshToken,
            });
            console.log('Token refresh successful.');
            localStorage.setItem('access_token', res.data.access);
            api.defaults.headers.common['Authorization'] = 'Bearer ' + res.data.access;
            return api(originalRequest);
          } catch (err) {
            console.error('Token refresh failed:', err);
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            console.log('Redirecting to /login.');
            window.location.href = '/login';
          }
        } else {
          console.log('No refresh token found.');
        }
      }
    } else {
      console.log('Error does not have a response object:', error.message);
    }

    return Promise.reject(error);
  }
);

export default api;
