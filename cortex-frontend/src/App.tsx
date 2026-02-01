import React from 'react'; // 确保引入 React
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { LoginPage } from './features/auth/LoginPage';
import { ProjectsPage } from './features/projects/ProjectsPage';
import { DashboardPage } from './features/dashboard/DashboardPage';
import { KanbanBoard } from './features/tasks/KanbanBoard';
import { TaskListPage } from './features/tasks/TaskListPage';
import { TaskDetailPage } from './features/tasks/TaskDetailPage';
import { TaskBoardPage } from './features/tasks/TaskBoardPage';
import { CreateTaskPage } from './features/tasks/CreateTaskPage';
import { MainLayout } from './components/layout/MainLayout';
import { ProfilePage } from './features/auth/ProfilePage';

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
            <Route path="/tasks" element={<TaskListPage />} />
            <Route path="/tasks/:taskId" element={<TaskDetailPage />} />
            <Route path="/tasks/new" element={<CreateTaskPage />} />
            <Route path="/board" element={<TaskBoardPage />} />
            <Route path="/profile" element={<ProfilePage />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;