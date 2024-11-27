// frontend/src/services/api.ts
import axios from 'axios';

const api = axios.create({
    baseURL: process.env.REACT_APP_API_URL || '/api'
});

// Add request interceptor for auth headers
api.interceptors.request.use((config) => {
    const passkey = localStorage.getItem('document_passkey');
    if (passkey) {
        config.headers['X-Document-Passkey'] = passkey;
    }
    return config;
});

// Add response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Clear auth data on unauthorized
            localStorage.removeItem('document_passkey');
            localStorage.removeItem('auth_token');
        }
        return Promise.reject(error);
    }
);