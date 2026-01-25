import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Typography, Table, Tag, Button, Space, Input, Select, Card, Breadcrumb } from 'antd';
import { SearchOutlined, EyeOutlined, BorderlessTableOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { getMyTasks } from './service';
import { getProjects } from '../projects/service';
import type { Task } from '../../types';
import type { Project } from '../../types';
import { TaskStatus, PaginationConfig } from '../../constants';
import { getStatusConfig, getPriorityConfig } from '../../utils';

const { Title } = Typography;
const { Option } = Select;

export const TaskListPage: React.FC = () => {
  const navigate = useNavigate();
  const [statusFilter, setStatusFilter] = useState<TaskStatus | 'ALL'>('ALL');
  const [priorityFilter, setPriorityFilter] = useState<string>('ALL');
  const [searchText, setSearchText] = useState('');

  const { data: tasks = [], isLoading: isLoadingTasks } = useQuery({
    queryKey: ['myTasks'],
    queryFn: getMyTasks,
  });

  const { data: projects = [], isLoading: isLoadingProjects } = useQuery({
    queryKey: ['projects'],
    queryFn: getProjects,
  });

  // 创建项目ID到项目名称的映射
  const projectNameMap = useMemo(() => {
    const map = new Map<number, string>();
    projects.forEach((project: Project) => {
      map.set(project.id, project.name);
    });
    return map;
  }, [projects]);

  const isLoading = isLoadingTasks || isLoadingProjects;

  // 过滤任务
  const filteredTasks = tasks.filter((task) => {
    const matchStatus = statusFilter === 'ALL' || task.status === statusFilter;
    const matchPriority = priorityFilter === 'ALL' || task.priority === priorityFilter;
    const matchSearch =
      !searchText ||
      task.title.toLowerCase().includes(searchText.toLowerCase()) ||
      (task.description?.toLowerCase().includes(searchText.toLowerCase()) ?? false);
    return matchStatus && matchPriority && matchSearch;
  });

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
      render: (id: number) => <span style={{ color: '#94a3b8' }}>#{id}</span>,
    },
    {
      title: '任务标题',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
      render: (title: string, record: Task) => (
        <a
          onClick={() => navigate(`/tasks/${record.id}`)}
          style={{ fontWeight: 500, color: '#1e293b' }}
        >
          {title}
        </a>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: TaskStatus) => {
        const config = getStatusConfig(status);
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      width: 100,
      render: (priority: string) => {
        const config = getPriorityConfig(priority);
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
    {
      title: '所属项目',
      dataIndex: 'project_id',
      key: 'project_id',
      width: 150,
      render: (projectId: number) => {
        const projectName = projectNameMap.get(projectId);
        return (
          <Tag color="blue" style={{ cursor: 'pointer' }} onClick={() => navigate(`/projects/${projectId}`)}>
            {projectName || `项目 ${projectId}`}
          </Tag>
        );
      },
    },
    {
      title: '操作',
      key: 'action',
      width: 180,
      render: (_: any, record: Task) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/tasks/${record.id}`)}
          >
            详情
          </Button>
          <Button
            type="link"
            size="small"
            icon={<BorderlessTableOutlined />}
            onClick={() => navigate(`/projects/${record.project_id}`)}
          >
            看板
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      {/* 页面标题与导航 */}
      <div style={{ marginBottom: 24 }}>
        <Breadcrumb
          items={[
            { title: <a onClick={() => navigate('/')}>工作台</a> },
            { title: '我的任务' },
          ]}
          style={{ marginBottom: 8 }}
        />
        <Title level={3} style={{ margin: 0 }}>我的任务</Title>
      </div>

      {/* 筛选与搜索 */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <Space size="middle" wrap>
          <Input
            placeholder="搜索任务标题或描述..."
            prefix={<SearchOutlined />}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            style={{ width: 280 }}
            allowClear
          />
          <Select
            placeholder="筛选状态"
            value={statusFilter}
            onChange={setStatusFilter}
            style={{ width: 140 }}
          >
            <Option value="ALL">全部状态</Option>
            <Option value={TaskStatus.TODO}>待处理</Option>
            <Option value={TaskStatus.IN_PROGRESS}>进行中</Option>
            <Option value={TaskStatus.REVIEW}>待审核</Option>
            <Option value={TaskStatus.DONE}>已完成</Option>
          </Select>
          <Select
            placeholder="筛选优先级"
            value={priorityFilter}
            onChange={setPriorityFilter}
            style={{ width: 140 }}
          >
            <Option value="ALL">全部优先级</Option>
            <Option value="HIGH">高</Option>
            <Option value="MEDIUM">中</Option>
            <Option value="LOW">低</Option>
          </Select>
          <div style={{ marginLeft: 'auto', color: '#94a3b8', fontSize: 14 }}>
            共 {filteredTasks.length} 个任务
          </div>
        </Space>
      </Card>

      {/* 任务表格 */}
      <Table
        columns={columns}
        dataSource={filteredTasks}
        rowKey="id"
        loading={isLoading}
        pagination={{
          pageSize: PaginationConfig.pageSize,
          showSizeChanger: true,
          showTotal: PaginationConfig.showTotal,
        }}
        style={{ background: '#fff', borderRadius: 8 }}
      />
    </div>
  );
};
