import axios from 'axios';
import { auth } from '../firebaseConfig';

const commonConfig = {
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
};

const api = axios.create(commonConfig);

export const api_unauthenticated = axios.create(commonConfig);

api.interceptors.request.use(
  async (config) => {
    const currentUser = auth.currentUser;
    if (currentUser) {
      const token = await currentUser.getIdToken();
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// The response interceptor for token refreshing is removed as Firebase handles token refreshing automatically.

export default api;
