// src/App.tsx
import React from 'react'; // 确保引入 React
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { LoginPage } from './features/auth/LoginPage';
import { ProjectsPage } from './features/projects/ProjectsPage';


// 路由守卫组件 (PrivateRoute)
// 使用 React.ReactNode 作为 children 的类型，容错率更高
const PrivateRoute = ({ children }: { children: React.ReactNode }) => {
  const token = localStorage.getItem('access_token');
  // 如果有 token 则渲染子组件，否则重定向到登录页
  return token ? <>{children}</> : <Navigate to="/login" replace />;
};

// 主应用组件
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
              <ProjectsPage />
            </PrivateRoute>
          } 
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;