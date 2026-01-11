import React from 'react'; // 确保引入 React
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from './lib/react-query';
import { LoginPage } from './features/auth/LoginPage';
import { ProjectsPage } from './features/projects/ProjectsPage';
import { DashboardPage } from './features/dashboard/DashboardPage';
import { KanbanBoard } from './features/tasks/KanbanBoard';
import { MainLayout } from './components/layout/MainLayout';
import { ProfilePage } from './features/auth/ProfilePage'; // Import ProfilePage

// 路由守卫组件 (PrivateRoute)
// 使用 React.ReactNode 作为 children 的类型，容错率更高
const PrivateRoute = ({ children }: { children?: React.ReactNode }) => {
  const token = localStorage.getItem('access_token');
  // 如果有 token 则渲染子组件或 Outlet，否则重定向到登录页
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children ? <>{children}</> : <Outlet />;
};

// 主应用组件
const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ConfigProvider
        theme={{
          token: {
            colorPrimary: '#6366f1',
            borderRadius: 8,
            fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif',
          },
        }}
      >
        <BrowserRouter>
          <Routes>
            {/* 公开路由：登录页 */}
            <Route path="/login" element={<LoginPage />} />

            {/* 受保护路由组：使用 MainLayout 包装 */}
            <Route element={<PrivateRoute />}>
              <Route element={<MainLayout><Outlet /></MainLayout>}>
                <Route path="/" element={<DashboardPage />} />
                <Route path="/projects" element={<ProjectsPage />} />
                <Route path="/projects/:projectId" element={<KanbanBoard />} />
                <Route path="/profile" element={<ProfilePage />} /> {/* Add ProfilePage route */}
              </Route>
            </Route>
          </Routes>
        </BrowserRouter>
      </ConfigProvider>
    </QueryClientProvider>
  );
}

export default App;