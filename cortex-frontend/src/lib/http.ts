import axios from 'axios';
import { message } from 'antd';

export const http = axios.create({
    baseURL: '/api/v1',
    timeout: 10000,
});

// 请求拦截器：自动注入 Token
http.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
})

// 响应拦截器：统一处理错误 (如 401 token 过期)
http.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            message.error('登录已过期，请重新登录');
            localStorage.removeItem('access_token');
            // 这里可以使用 window.location 跳转，或者在组件层通过 navigate 跳转
            window.location.href = '/login';
        } else {
            message.error(error.response?.data?.detail || '网络请求错误');
        }
        return Promise.reject(error);
    }
)