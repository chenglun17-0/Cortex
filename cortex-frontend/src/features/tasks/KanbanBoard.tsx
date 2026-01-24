import React, { useMemo, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Typography, Card, Spin, Tag, Button, Modal, Form, Input, Select, message, Space, Breadcrumb, Avatar, Tooltip, DatePicker, Drawer, List, Popconfirm } from 'antd';
import { PlusOutlined, MoreOutlined, ClockCircleOutlined, TeamOutlined, UserAddOutlined, UserDeleteOutlined, SearchOutlined } from '@ant-design/icons';
import { DragDropContext, Droppable, Draggable, type DropResult } from '@hello-pangea/dnd';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getTasksByProject, updateTask, createTask } from './service';
import { getProjects, getProjectMembers, addProjectMember, removeProjectMember, searchUsers } from '../projects/service';
import { type Task, TaskStatus, type Project, type User } from '../../types';


const { Title, Text } = Typography;
const { Option } = Select;

// 定义看板的列结构
const COLUMNS = [
    { id: TaskStatus.TODO, title: '待处理', color: '#64748b' },
    { id: TaskStatus.IN_PROGRESS, title: '进行中', color: '#3b82f6' },
    { id: TaskStatus.REVIEW, title: '待审核', color: '#f59e0b' },
    { id: TaskStatus.DONE, title: '已完成', color: '#10b981' },
];

const PriorityTag: React.FC<{ priority: string }> = ({ priority }) => {
  const colors: Record<string, string> = {
    HIGH: 'red',
    MEDIUM: 'orange',
    LOW: 'blue',
  };
  const textMap: Record<string, string> = {
    HIGH: '高',
    MEDIUM: '中',
    LOW: '低',
  };
  return (
    <Tag color={colors[priority] || 'default'} variant="filled" style={{ fontSize: '10px', lineHeight: '16px' }}>
      {textMap[priority] || priority}
    </Tag>
  );
};

export const KanbanBoard: React.FC = () => {
    const { projectId } = useParams<{ projectId: string }>();
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [memberDrawerOpen, setMemberDrawerOpen] = useState(false);
    const [searchKeyword, setSearchKeyword] = useState('');
    const [form] = Form.useForm();
    const searchInputRef = useRef<any>(null);

    const { data: tasks = [], isLoading: isLoadingTasks } = useQuery({
        queryKey: ['tasks', projectId],
        queryFn: () => getTasksByProject(projectId!),
        enabled: !!projectId,
    });

    const { data: projects = [], isLoading: isLoadingProjects } = useQuery({
        queryKey: ['projects'],
        queryFn: getProjects,
    });

    // 查找当前项目
    const currentProject = useMemo(() => {
        return projects.find((p: Project) => p.id === Number(projectId));
    }, [projects, projectId]);

    const isLoading = isLoadingTasks || isLoadingProjects;

    // 成员管理
    const { data: members = [], refetch: refetchMembers } = useQuery({
        queryKey: ['projectMembers', projectId],
        queryFn: () => getProjectMembers(Number(projectId)),
        enabled: !!projectId && memberDrawerOpen,
    });

    const { data: searchResults = [], isLoading: isSearching } = useQuery({
        queryKey: ['userSearch', searchKeyword],
        queryFn: () => searchUsers(searchKeyword),
        enabled: searchKeyword.length > 0,
    });

    const addMemberMutation = useMutation({
        mutationFn: ({ projectId, userId }: { projectId: number; userId: number }) =>
            addProjectMember(projectId, userId),
        onSuccess: () => {
            message.success('成员添加成功');
            queryClient.invalidateQueries({ queryKey: ['projectMembers', projectId] });
            queryClient.invalidateQueries({ queryKey: ['projects'] });
            setSearchKeyword('');
        },
        onError: () => {
            message.error('添加失败');
        }
    });

    const removeMemberMutation = useMutation({
        mutationFn: ({ projectId, userId }: { projectId: number; userId: number }) =>
            removeProjectMember(projectId, userId),
        onSuccess: () => {
            message.success('成员已移除');
            queryClient.invalidateQueries({ queryKey: ['projectMembers', projectId] });
            queryClient.invalidateQueries({ queryKey: ['projects'] });
        },
        onError: () => {
            message.error('移除失败');
        }
    });

    const updateTaskMutation = useMutation({
        mutationFn: ({ id, status }: { id: number; status: TaskStatus }) =>
            updateTask(id, { status }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['tasks', projectId] });
        },
    });

    const createTaskMutation = useMutation({
        mutationFn: createTask,
        onSuccess: () => {
            message.success('任务创建成功');
            setIsModalOpen(false);
            form.resetFields();
            queryClient.invalidateQueries({ queryKey: ['tasks', projectId] });
        },
        onError: () => {
            message.error('创建失败');
        }
    });

    const handleCreate = (values: any) => {
        if (!projectId) return;
        createTaskMutation.mutate({
            ...values,
            project_id: Number(projectId),
            status: TaskStatus.TODO,
            deadline: values.deadline?.format('YYYY-MM-DD'),
        });
    };

    const handleSearchUser = (keyword: string) => {
        setSearchKeyword(keyword);
    };

    const handleAddMember = (userId: number) => {
        if (!projectId) return;
        addMemberMutation.mutate({ projectId: Number(projectId), userId });
    };

    const handleRemoveMember = (userId: number) => {
        if (!projectId) return;
        removeMemberMutation.mutate({ projectId: Number(projectId), userId });
    };

    const tasksByStatus = useMemo(() => {
        const grouped: Record<string, Task[]> = {
            [TaskStatus.TODO]: [],
            [TaskStatus.IN_PROGRESS]: [],
            [TaskStatus.REVIEW]: [],
            [TaskStatus.DONE]: [],
        };
        tasks.forEach((task) => {
            if (grouped[task.status]) {
                grouped[task.status].push(task);
            }
        });
        return grouped;
    }, [tasks]);

    const onDragEnd = (result: DropResult) => {
        const { source, destination, draggableId } = result;
        if (!destination) return;
        if (source.droppableId === destination.droppableId && source.index === destination.index) return;

        updateTaskMutation.mutate({
            id: Number(draggableId),
            status: destination.droppableId as TaskStatus,
        });
    };

    if (isLoading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;

    // 已添加的成员 ID 集合，用于过滤搜索结果
    const addedMemberIds = new Set(members.map((m: User) => m.id));
    const availableSearchResults = searchResults.filter((u: User) => !addedMemberIds.has(u.id));

    return (
        <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            {/* 顶部导航与操作 */}
            <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <Breadcrumb
                    items={[
                      { title: <a onClick={() => navigate('/')}>工作台</a> },
                      { title: <a onClick={() => navigate('/projects')}>项目列表</a> },
                      { title: currentProject?.name || `项目 ${projectId}` },
                    ]}
                    style={{ marginBottom: 8 }}
                  />
                  <Title level={3} style={{ margin: 0 }}>{currentProject?.name || `项目 ${projectId}`}</Title>
                </div>

                <Space>
                    <Button
                        icon={<TeamOutlined />}
                        onClick={() => setMemberDrawerOpen(true)}
                        style={{ borderRadius: 8 }}
                    >
                        成员管理 ({members.length})
                    </Button>
                    <Button
                        type="primary"
                        icon={<PlusOutlined />}
                        onClick={() => setIsModalOpen(true)}
                        size="large"
                        style={{ borderRadius: 8 }}
                    >
                        新建任务
                    </Button>
                </Space>
            </div>

            {/* 成员管理抽屉 */}
            <Drawer
                title="项目成员管理"
                size="small"
                open={memberDrawerOpen}
                onClose={() => setMemberDrawerOpen(false)}
            >
                {/* 搜索添加成员 */}
                <div style={{ marginBottom: 16 }}>
                    <Text strong style={{ display: 'block', marginBottom: 8 }}>添加成员</Text>
                    <Input
                        ref={searchInputRef}
                        placeholder="搜索用户名..."
                        prefix={<SearchOutlined />}
                        value={searchKeyword}
                        onChange={(e) => handleSearchUser(e.target.value)}
                        allowClear
                    />
                    {searchKeyword && (
                        <List
                            size="small"
                            dataSource={availableSearchResults}
                            loading={isSearching}
                            style={{ marginTop: 8, maxHeight: 200, overflow: 'auto', border: '1px solid #f0f0f0', borderRadius: 8 }}
                            renderItem={(user: User) => (
                                <List.Item
                                    actions={[
                                        <Button
                                            type="primary"
                                            size="small"
                                            icon={<UserAddOutlined />}
                                            onClick={() => handleAddMember(user.id)}
                                        >
                                            添加
                                        </Button>
                                    ]}
                                >
                                    <List.Item.Meta
                                        title={user.username}
                                        description={user.email}
                                        avatar={<Avatar size="small" icon={<UserOutlined />} />}
                                    />
                                </List.Item>
                            )}
                        />
                    )}
                </div>

                {/* 成员列表 */}
                <Text strong style={{ display: 'block', marginBottom: 8 }}>当前成员 ({members.length})</Text>
                <List
                    dataSource={members}
                    renderItem={(user: User) => (
                        <List.Item
                            actions={[
                                <Popconfirm
                                    title="确定要移除此成员吗？"
                                    onConfirm={() => handleRemoveMember(user.id)}
                                    okText="确定"
                                    cancelText="取消"
                                >
                                    <Button
                                        type="text"
                                        danger
                                        size="small"
                                        icon={<UserDeleteOutlined />}
                                    />
                                </Popconfirm>
                            ]}
                        >
                            <List.Item.Meta
                                title={user.username}
                                description={user.email}
                                avatar={<Avatar size="small" style={{ backgroundColor: '#6366f1' }}>{user.username[0]?.toUpperCase()}</Avatar>}
                            />
                        </List.Item>
                    )}
                />
            </Drawer>


            {/* 拖拽上下文 */}
            <DragDropContext onDragEnd={onDragEnd}>
                <div style={{ display: 'flex', gap: '20px', alignItems: 'flex-start', overflowX: 'auto', paddingBottom: 16, flex: 1 }}>
                    {COLUMNS.map((col) => (
                        <Droppable key={col.id} droppableId={col.id}>
                            {(provided, snapshot) => (
                                <div
                                    ref={provided.innerRef}
                                    {...provided.droppableProps}
                                    style={{
                                        background: '#f8fafc',
                                        padding: '12px',
                                        borderRadius: '12px',
                                        width: '320px',
                                        minHeight: '600px',
                                        display: 'flex',
                                        flexDirection: 'column',
                                        border: '1px solid #e2e8f0',
                                        boxShadow: snapshot.isDraggingOver ? '0 0 0 2px #6366f1' : 'none',
                                        transition: 'background-color 0.2s ease',
                                    }}
                                >
                                    {/* 列标题 */}
                                    <div style={{ padding: '4px 8px 16px', fontWeight: 600, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                        <Space size={8}>
                                          <div style={{ width: 8, height: 8, borderRadius: '50%', background: col.color }} />
                                          <span style={{ color: '#475569', fontSize: 15 }}>{col.title}</span>
                                          <span style={{
                                            margin: 0,
                                            borderRadius: 10,
                                            background: '#e2e8f0',
                                            color: '#64748b',
                                            fontSize: 11,
                                            padding: '2px 6px',
                                          }}>
                                            {tasksByStatus[col.id]?.length || 0}
                                          </span>
                                        </Space>
                                        <Button type="text" size="small" icon={<MoreOutlined />} />
                                    </div>

                                    {/* 任务卡片列表 */}
                                    <div style={{ flex: 1 }}>
                                      {tasksByStatus[col.id]?.map((task, index) => (
                                          <Draggable key={task.id} draggableId={String(task.id)} index={index}>
                                              {(provided, snapshot) => (
                                                  <Card
                                                      ref={provided.innerRef}
                                                      {...provided.draggableProps}
                                                      {...provided.dragHandleProps}
                                                      size="small"
                                                      variant="borderless"
                                                      style={{
                                                          marginBottom: '12px',
                                                          borderRadius: '8px',
                                                          boxShadow: snapshot.isDragging
                                                            ? '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
                                                            : '0 1px 3px rgba(0, 0, 0, 0.05)',
                                                          border: '1px solid #e2e8f0',
                                                          background: '#fff',
                                                          ...provided.draggableProps.style,
                                                      }}
                                                      styles={{ body: { padding: '12px' } }}
                                                  >
                                                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                                                        <Text style={{ fontSize: 12, color: '#94a3b8', fontWeight: 500 }}>#{task.id}</Text>
                                                        <PriorityTag priority={task.priority || "MEDIUM"} />
                                                      </div>
                                                      <div style={{ fontWeight: 600, color: '#1e293b', marginBottom: 12, lineHeight: 1.5 }}>
                                                        {task.title}
                                                      </div>
                                                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                                        <Tooltip title="截止日期未设置">
                                                          <Space size={4} style={{ fontSize: 12, color: '#94a3b8' }}>
                                                            <ClockCircleOutlined style={{ fontSize: 10 }} />
                                                            <span>-</span>
                                                          </Space>
                                                        </Tooltip>
                                                        <Avatar size={20} style={{ backgroundColor: '#6366f1', fontSize: 10 }}>U</Avatar>
                                                      </div>
                                                  </Card>
                                              )}
                                          </Draggable>
                                      ))}
                                      {provided.placeholder}
                                    </div>
                                </div>
                            )}
                        </Droppable>
                    ))}
                </div>
            </DragDropContext>

            {/* 新建任务弹窗 */}
            <Modal
                title="新建任务"
                open={isModalOpen}
                onOk={() => form.submit()}
                onCancel={() => setIsModalOpen(false)}
                confirmLoading={createTaskMutation.isPending}
                okButtonProps={{ style: { borderRadius: 6 } }}
                cancelButtonProps={{ style: { borderRadius: 6 } }}
            >
                <Form form={form} layout="vertical" onFinish={handleCreate}>
                    <Form.Item
                        name="title"
                        label="任务标题"
                        rules={[{ required: true, message: '请输入任务标题' }]}
                    >
                        <Input placeholder="例如：实现登录接口" style={{ borderRadius: 6 }} />
                    </Form.Item>

                    <Form.Item
                        name="type"
                        label="任务类型"
                        initialValue="feature"
                        rules={[{ required: true, message: '请选择任务类型' }]}
                    >
                        <Select style={{ borderRadius: 6 }}>
                            <Option value="feature">新功能 (feature)</Option>
                            <Option value="bug">Bug 修复 (bug)</Option>
                            <Option value="docs">文档更新 (docs)</Option>
                            <Option value="fix">修复 (fix)</Option>
                            <Option value="chore">构建 (chore)</Option>
                            <Option value="refactor">重构 (refactor)</Option>
                        </Select>
                    </Form.Item>

                    <Form.Item name="priority" label="优先级" initialValue="MEDIUM">
                        <Select style={{ borderRadius: 6 }}>
                            <Option value="HIGH">高 (High)</Option>
                            <Option value="MEDIUM">中 (Medium)</Option>
                            <Option value="LOW">低 (Low)</Option>
                        </Select>
                    </Form.Item>

                    <Form.Item
                        name="deadline"
                        label="截止日期"
                        rules={[{ required: true, message: '请选择截止日期' }]}
                    >
                        <DatePicker
                            style={{ width: '100%', borderRadius: 6 }}
                            placeholder="选择截止日期"
                            format="YYYY-MM-DD"
                            disabledDate={(current: any) => {
                                return current && current < new Date();
                            }}
                        />
                    </Form.Item>

                    <Form.Item name="description" label="详细描述">
                        <Input.TextArea rows={4} placeholder="输入项目描述..." style={{ borderRadius: 6 }} />
                    </Form.Item>
                </Form>
            </Modal>
        </div>
    );
};