import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClientProvider } from '@tanstack/react-query';
import { ConfigProvider } from 'antd';
import znCN from 'antd/locale/zh_CN';
import App from './App.tsx';
import { queryClient } from './lib/react-query.ts';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <ConfigProvider locale={znCN}>
        <App />
      </ConfigProvider>
    </QueryClientProvider>
  </React.StrictMode>
)