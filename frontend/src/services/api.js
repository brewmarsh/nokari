import axios from 'axios';

const commonConfig = {
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
};

const api = axios.create(commonConfig);

export const api_unauthenticated = axios.create(commonConfig);

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');

      if (refreshToken) {
        try {
          const { data } = await api_unauthenticated.post('/login/refresh/', {
            refresh: refreshToken,
          });
          localStorage.setItem('access_token', data.access);
          api.defaults.headers.common['Authorization'] = `Bearer ${data.access}`;
          return api(originalRequest);
        } catch (err) {
          console.error('Token refresh failed:', err);
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      } else {
        // No refresh token, redirect to login
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

export default api;
