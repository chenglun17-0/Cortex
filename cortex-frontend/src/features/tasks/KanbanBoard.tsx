import React, { useMemo, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Layout, Typography, Card, Spin, Tag, Button, Modal, Form, Input, Select, message, } from 'antd';
import { ArrowLeftOutlined, PlusOutlined } from '@ant-design/icons';
import { DragDropContext, Droppable, Draggable, type DropResult } from '@hello-pangea/dnd';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getTasksByProject, updateTask, createTask } from './service';
import { type Task, TaskStatus } from '../../types';


const { Content } = Layout;
const { Title } = Typography;
const { Option } = Select;

// 定义看板的列结构
const COLUMNS = [
    { id: TaskStatus.TODO, title: '待处理', color: '#f50' },
    { id: TaskStatus.IN_PROGRESS, title: '进行中', color: '#2db7f5' },
    { id: TaskStatus.REVIEW, title: '待审核', color: '#87d068' },
    { id: TaskStatus.DONE, title: '已完成', color: '#108ee9' },
];

export const KanbanBoard: React.FC = () => {
    const { projectId } = useParams<{ projectId: string }>();
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [form] = Form.useForm();
    // 获取任务数据
    const { data: tasks = [], isLoading } = useQuery({
        queryKey: ['tasks', projectId],
        queryFn: () => getTasksByProject(projectId!),
        enabled: !!projectId, // 只有 projectId 存在时才请求
    });

    // 乐观更新 (Mutation)：拖拽后立即更新 UI，随后异步请求后端
    const updateTaskMutation = useMutation({
        mutationFn: ({ id, status }: { id: number; status: TaskStatus }) =>
            updateTask(id, { status }),
        onSuccess: () => {
            // 成功后让缓存失效，触发重新拉取确保数据一致
            queryClient.invalidateQueries({ queryKey: ['tasks', projectId] });
        },
    });

    // 创建任务 Mutation
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

    // 处理表单提交
    const handleCreate = (values: any) => {
        if (!projectId) return;
        createTaskMutation.mutate({
            ...values,
            project_id: Number(projectId), // 确保转为数字
            status: TaskStatus.TODO,       // 默认状态
        });
    };

    // 将扁平的任务列表按状态分组
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

    // 处理拖拽结束事件
    const onDragEnd = (result: DropResult) => {
        const { source, destination, draggableId } = result;

        // 如果没有放置目标，或者位置没变，直接返回
        if (!destination) return;
        if (
            source.droppableId === destination.droppableId &&
            source.index === destination.index
        ) {
            return;
        }

        // 触发更新
        // 注意：这里 draggableId 通常是 string，需要转为 number
        updateTaskMutation.mutate({
            id: Number(draggableId),
            status: destination.droppableId as TaskStatus,
        });

        // 💡 进阶提示：为了体验更好，这里可以使用 queryClient.setQueryData 做乐观 UI 更新
        // 但为了代码简单，暂时先依赖 React Query 的自动刷新
    };

    if (isLoading) return <Spin size="large" style={{ display: 'block', margin: '50px auto' }} />;

    return (
        <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
            <Content style={{ padding: '24px', overflowX: 'auto' }}>
                {/* 顶部导航栏*/}
                <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                        <Button type="link" icon={<ArrowLeftOutlined />} onClick={() => navigate('/')} style={{ paddingLeft: 0 }}>
                            返回项目列表
                        </Button>
                        <Title level={3} style={{ marginTop: 0, marginBottom: 0 }}>项目看板 (ID: {projectId})</Title>
                    </div>

                    <Button
                        type="primary"
                        icon={<PlusOutlined />}
                        onClick={() => setIsModalOpen(true)}
                    >
                        新建任务
                    </Button>
                </div>


                {/* 拖拽上下文 */}
                <DragDropContext onDragEnd={onDragEnd}>
                    <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-start', minWidth: '1000px' }}>
                        {COLUMNS.map((col) => (
                            <Droppable key={col.id} droppableId={col.id}>
                                {(provided, snapshot) => (
                                    <div
                                        ref={provided.innerRef}
                                        {...provided.droppableProps}
                                        style={{
                                            background: '#ebecf0',
                                            padding: '16px',
                                            borderRadius: '8px',
                                            width: '300px',
                                            minHeight: '500px',
                                            display: 'flex',
                                            flexDirection: 'column',
                                        }}
                                    >
                                        {/* 列标题 */}
                                        <div style={{ marginBottom: 16, fontWeight: 'bold', display: 'flex', justifyContent: 'space-between' }}>
                                            <span>{col.title}</span>
                                            <Tag color={col.color}>{tasksByStatus[col.id]?.length || 0}</Tag>
                                        </div>

                                        {/* 任务卡片列表 */}
                                        {tasksByStatus[col.id]?.map((task, index) => (
                                            <Draggable key={task.id} draggableId={String(task.id)} index={index}>
                                                {(provided, snapshot) => (
                                                    <Card
                                                        ref={provided.innerRef}
                                                        {...provided.draggableProps}
                                                        {...provided.dragHandleProps}
                                                        size="small"
                                                        style={{
                                                            marginBottom: '8px',
                                                            boxShadow: snapshot.isDragging ? '0 5px 10px rgba(0,0,0,0.2)' : 'none',
                                                            ...provided.draggableProps.style, // 必须保留这个 style
                                                        }}
                                                    >
                                                        <div style={{ fontWeight: 500 }}>{task.title}</div>
                                                        <div style={{ color: '#888', fontSize: '12px', marginTop: 4 }}>
                                                            ID: #{task.id}
                                                        </div>
                                                    </Card>
                                                )}
                                            </Draggable>
                                        ))}
                                        {provided.placeholder}
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
                >
                    <Form form={form} layout="vertical" onFinish={handleCreate}>
                        <Form.Item
                            name="title"
                            label="任务标题"
                            rules={[{ required: true, message: '请输入任务标题' }]}
                        >
                            <Input placeholder="例如：实现登录接口" />
                        </Form.Item>

                        <Form.Item name="priority" label="优先级" initialValue="Medium">
                            <Select>
                                <Option value="High">高 (High)</Option>
                                <Option value="Medium">中 (Medium)</Option>
                                <Option value="Low">低 (Low)</Option>
                            </Select>
                        </Form.Item>

                        <Form.Item name="description" label="详细描述">
                            <Input.TextArea rows={4} placeholder="支持 Markdown 格式..." />
                        </Form.Item>
                    </Form>
                </Modal>
            </Content>
        </Layout>
    );
};