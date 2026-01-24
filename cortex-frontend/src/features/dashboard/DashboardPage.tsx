import React from 'react';
import { Typography, Card, List, Statistic, Row, Col, Tag, Button, Empty, Space } from 'antd';
import { 
    CheckCircleOutlined, 
    ProjectOutlined, 
    RightOutlined, 
    ClockCircleOutlined 
} from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { getMyTasks } from '../tasks/service';
import { getProjects } from '../projects/service';
import { getCurrentUser } from '../auth/service';
import { TaskStatus } from '../../types';

const { Title, Text } = Typography;

export const DashboardPage: React.FC = () => {
    const navigate = useNavigate();

    // Fetch current user
    const { data: user } = useQuery({
        queryKey: ['me'],
        queryFn: getCurrentUser,
    });
    
    // Fetch user's tasks
    const { data: myTasks = [], isLoading: tasksLoading } = useQuery({
        queryKey: ['myTasks'],
        queryFn: getMyTasks,
    });

    // Fetch user's projects (for stats)
    const { data: projects = [], isLoading: projectsLoading } = useQuery({
        queryKey: ['projects'],
        queryFn: getProjects,
    });

    // Calculate stats
    const pendingTasksCount = myTasks.filter(t => t.status !== TaskStatus.DONE).length;
    const completedTasksCount = myTasks.filter(t => t.status === TaskStatus.DONE).length;
    
    // Priority colors helper
    const getPriorityColor = (priority?: string) => {
        switch (priority) {
            case 'High': return 'red';
            case 'Medium': return 'orange';
            case 'Low': return 'blue';
            default: return 'default';
        }
    };

    // Status colors helper
    const getStatusColor = (status: string) => {
        switch (status) {
            case TaskStatus.TODO: return 'default';
            case TaskStatus.IN_PROGRESS: return 'processing';
            case TaskStatus.REVIEW: return 'warning';
            case TaskStatus.DONE: return 'success';
            default: return 'default';
        }
    };

    const getStatusText = (status: string) => {
        switch (status) {
            case TaskStatus.TODO: return '待处理';
            case TaskStatus.IN_PROGRESS: return '进行中';
            case TaskStatus.REVIEW: return '待审核';
            case TaskStatus.DONE: return '已完成';
            default: return status;
        }
    };

    return (
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
            {/* Header Section */}
            <div style={{ marginBottom: 32 }}>
                <Title level={2} style={{ marginBottom: 8 }}>
                    欢迎回来，{user?.username || 'User'}
                </Title>
                <Text type="secondary">
                    您有 {pendingTasksCount} 个待处理任务和 {projects.length} 个参与的项目。
                </Text>
            </div>

            {/* Stats Cards */}
            <Row gutter={24} style={{ marginBottom: 32 }}>
                <Col span={8}>
                    <Card variant="borderless" style={{ borderRadius: 12, boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
                        <Statistic
                            title="待处理任务"
                            value={pendingTasksCount}
                            prefix={<ClockCircleOutlined style={{ color: '#f59e0b' }} />}
                            styles={{ content: { color: '#1e293b', fontWeight: 600 } }}
                        />
                    </Card>
                </Col>
                <Col span={8}>
                    <Card variant="borderless" style={{ borderRadius: 12, boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
                        <Statistic
                            title="参与项目"
                            value={projects.length}
                            prefix={<ProjectOutlined style={{ color: '#3b82f6' }} />}
                            styles={{ content: { color: '#1e293b', fontWeight: 600 } }}
                        />
                    </Card>
                </Col>
                <Col span={8}>
                    <Card variant="borderless" style={{ borderRadius: 12, boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
                        <Statistic
                            title="已完成任务"
                            value={completedTasksCount}
                            prefix={<CheckCircleOutlined style={{ color: '#10b981' }} />}
                            styles={{ content: { color: '#1e293b', fontWeight: 600 } }}
                        />
                    </Card>
                </Col>
            </Row>

            {/* My Tasks List */}
            <Row gutter={24}>
                <Col span={16}>
                    <Card
                        title="我的任务"
                        variant="borderless"
                        style={{ borderRadius: 12, boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}
                        extra={<Button type="link" onClick={() => navigate('/projects')}>查看所有项目</Button>}
                    >
                        <List
                            loading={tasksLoading}
                            dataSource={myTasks.filter(t => t.status !== TaskStatus.DONE).slice(0, 5)}
                            locale={{ emptyText: <Empty description="暂无待办任务" /> }}
                            renderItem={(item) => (
                                <List.Item
                                    actions={[
                                        <Button
                                            type="text"
                                            size="small"
                                            key="view"
                                            onClick={() => navigate(`/projects/${item.project_id}`)}
                                        >
                                            查看 <RightOutlined />
                                        </Button>
                                    ]}
                                >
                                    <List.Item.Meta
                                        avatar={
                                            <div style={{
                                                width: 8,
                                                height: 8,
                                                borderRadius: '50%',
                                                backgroundColor: getPriorityColor(item.priority),
                                                marginTop: 8
                                            }} />
                                        }
                                        title={<Text strong>{item.title}</Text>}
                                        description={
                                            <Space size={0} split={<span style={{ margin: '0 8px', color: '#cbd5e1' }}>|</span>}>
                                                <Text type="secondary" style={{ fontSize: 12 }}>ID: #{item.id}</Text>
                                                <Tag color={getStatusColor(item.status)} variant="filled" style={{ margin: 0 }}>
                                                    {getStatusText(item.status)}
                                                </Tag>
                                                {item.priority && (
                                                    <Tag color={getPriorityColor(item.priority)} variant="filled" style={{ margin: 0 }}>
                                                        {item.priority}
                                                    </Tag>
                                                )}
                                            </Space>
                                        }
                                    />
                                </List.Item>
                            )}
                        />
                    </Card>
                </Col>

                {/* Right Column: Recent Projects or Quick Actions (Placeholder) */}
                <Col span={8}>
                    <Card
                        title="最近项目"
                        variant="borderless"
                        style={{ borderRadius: 12, boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}
                    >
                        <List
                            loading={projectsLoading}
                            dataSource={projects.slice(0, 5)}
                            renderItem={(item) => (
                                <List.Item
                                    style={{ cursor: 'pointer', padding: '12px 0' }}
                                    onClick={() => navigate(`/projects/${item.id}`)}
                                >
                                    <div style={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                                        <ProjectOutlined style={{ fontSize: 18, color: '#94a3b8', marginRight: 12 }} />
                                        <div style={{ flex: 1, overflow: 'hidden' }}>
                                            <div style={{ fontWeight: 500, color: '#334155' }}>{item.name}</div>
                                        </div>
                                        <RightOutlined style={{ fontSize: 12, color: '#cbd5e1' }} />
                                    </div>
                                </List.Item>
                            )}
                        />
                    </Card>
                </Col>
            </Row>
        </div>
    );
};