// src/App.tsx
import React from 'react'; // 确保引入 React
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { LoginPage } from './features/auth/LoginPage';
import { Layout, Button } from 'antd'; // 引入 Button 组件

// 1. 临时主页组件 (DashboardPlaceholder)
const DashboardPlaceholder: React.FC = () => {
  const logout = () => {
    localStorage.removeItem('access_token');
    window.location.href = '/login';
  };

  return (
    <Layout style={{ padding: '50px', textAlign: 'center', height: '100vh' }}>
      <h1>🎉 欢迎进入 Cortex 看板</h1>
      <p>这里将展示项目列表和任务看板</p>
      <div style={{ marginTop: 20 }}>
        <Button type="primary" danger onClick={logout}>
          退出登录
        </Button>
      </div>
    </Layout>
  );
};

// 2. 路由守卫组件 (PrivateRoute)
// 使用 React.ReactNode 作为 children 的类型，容错率更高
const PrivateRoute = ({ children }: { children: React.ReactNode }) => {
  const token = localStorage.getItem('access_token');
  // 如果有 token 则渲染子组件，否则重定向到登录页
  return token ? <>{children}</> : <Navigate to="/login" replace />;
};

// 3. 主应用组件
const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* 公开路由：登录页 */}
        <Route path="/login" element={<LoginPage />} />

        {/* 受保护路由：主页 */}
        <Route 
          path="/" 
          element={
            <PrivateRoute>
              <DashboardPlaceholder />
            </PrivateRoute>
          } 
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;