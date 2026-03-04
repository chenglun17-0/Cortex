import { useMemo, useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Typography, Card, Spin, Tag, Select, Space, Breadcrumb, Button, Modal, Form, Input, DatePicker, message, Alert, List } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { DragDropContext, Droppable, Draggable, type DropResult } from '@hello-pangea/dnd';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getMyTasks, updateTask, createTask } from './service';
import { getProjects } from '../projects/service';
import { searchSimilarTasks } from './similarityService';
import type { Task } from '../../types';
import type { Project } from '../../types';
import { TaskStatus, KanbanColumns } from '../../constants';
import { getPriorityConfig } from '../../utils';
import dayjs, { type Dayjs } from 'dayjs';

const { Title } = Typography;
const { Option } = Select;
const { TextArea } = Input;

type CreateTaskFormValues = {
  title: string;
  description?: string;
  project_id: number;
  priority?: string;
  deadline?: Dayjs;
  type?: string;
};

type SimilarTaskItem = {
  task_id: number;
  title: string;
  similarity: number;
  project_id: number;
};

// PriorityTag 组件 - 使用统一的优先级配置
const PriorityTag: React.FC<{ priority?: string }> = ({ priority }) => {
  const config = getPriorityConfig(priority);
  return (
    <Tag color={config.color} variant="filled" style={{ fontSize: '10px', lineHeight: '16px' }}>
      {config.text}
    </Tag>
  );
};

export const TaskBoardPage: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [form] = Form.useForm();
  const [projectFilter, setProjectFilter] = useState<number | 'ALL'>('ALL');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [draftTitle, setDraftTitle] = useState('');
  const [draftDescription, setDraftDescription] = useState('');
  const [similarTasks, setSimilarTasks] = useState<SimilarTaskItem[]>([]);
  const [isSearchingSimilar, setIsSearchingSimilar] = useState(false);
  const [searchTriggered, setSearchTriggered] = useState(false);
  const [similarSearchError, setSimilarSearchError] = useState<string | null>(null);
  const similarSearchSeqRef = useRef(0);

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

  const updateTaskMutation = useMutation({
    mutationFn: ({ id, status }: { id: number; status: TaskStatus }) =>
      updateTask(id, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['myTasks'] });
    },
  });

  const createTaskMutation = useMutation({
    mutationFn: createTask,
    onSuccess: () => {
      message.success('任务创建成功');
      setIsCreateModalOpen(false);
      form.resetFields();
      setDraftTitle('');
      setDraftDescription('');
      setSimilarTasks([]);
      setSearchTriggered(false);
      setSimilarSearchError(null);
      queryClient.invalidateQueries({ queryKey: ['myTasks'] });
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
    onError: () => {
      message.error('创建失败');
    },
  });

  // 过滤任务
  const filteredTasks = useMemo(() => {
    if (projectFilter === 'ALL') return tasks;
    return tasks.filter((task) => task.project_id === projectFilter);
  }, [tasks, projectFilter]);

  // 获取所有项目ID用于筛选
  const projectIds = useMemo(() => {
    const ids = [...new Set(tasks.map((task) => task.project_id))];
    return ids.sort((a, b) => a - b);
  }, [tasks]);

  const tasksByStatus = useMemo(() => {
    const grouped: Record<string, Task[]> = {
      [TaskStatus.TODO]: [],
      [TaskStatus.IN_PROGRESS]: [],
      [TaskStatus.REVIEW]: [],
      [TaskStatus.DONE]: [],
    };
    filteredTasks.forEach((task) => {
      if (grouped[task.status]) {
        grouped[task.status].push(task);
      }
    });
    return grouped;
  }, [filteredTasks]);

  const onDragEnd = (result: DropResult) => {
    const { source, destination, draggableId } = result;
    if (!destination) return;
    if (source.droppableId === destination.droppableId && source.index === destination.index) return;

    updateTaskMutation.mutate({
      id: Number(draggableId),
      status: destination.droppableId as TaskStatus,
    });
  };

  const handleTaskClick = (taskId: number) => {
    navigate(`/tasks/${taskId}`);
  };

  const handleProjectClick = (e: React.MouseEvent, projectId: number) => {
    e.stopPropagation();
    navigate(`/projects/${projectId}`);
  };

  const searchSimilar = useCallback(
    async (title: string, description: string) => {
      const trimmedTitle = title.trim();
      if (trimmedTitle.length < 3) {
        similarSearchSeqRef.current += 1;
        setSimilarTasks([]);
        setSearchTriggered(false);
        setSimilarSearchError(null);
        return;
      }

      const currentSeq = similarSearchSeqRef.current + 1;
      similarSearchSeqRef.current = currentSeq;

      setIsSearchingSimilar(true);
      setSearchTriggered(true);
      setSimilarSearchError(null);

      try {
        const text = `${trimmedTitle}\n${description.trim()}`;
        const response = await searchSimilarTasks({
          text,
          limit: 3,
          threshold: 0.5,
        });
        if (currentSeq !== similarSearchSeqRef.current) {
          return;
        }
        setSimilarTasks(response.success ? response.results : []);
      } catch {
        if (currentSeq !== similarSearchSeqRef.current) {
          return;
        }
        setSimilarTasks([]);
        setSimilarSearchError('语义查重失败，请稍后重试');
      } finally {
        if (currentSeq === similarSearchSeqRef.current) {
          setIsSearchingSimilar(false);
        }
      }
    },
    [],
  );

  useEffect(() => {
    if (!isCreateModalOpen) {
      similarSearchSeqRef.current += 1;
      setIsSearchingSimilar(false);
      return;
    }
    const timer = setTimeout(() => {
      searchSimilar(draftTitle, draftDescription);
    }, 500);

    return () => clearTimeout(timer);
  }, [isCreateModalOpen, draftTitle, draftDescription, searchSimilar]);

  const openCreateTaskModal = () => {
    if (projectFilter !== 'ALL') {
      form.setFieldsValue({ project_id: projectFilter });
    } else {
      form.resetFields();
    }
    setDraftTitle('');
    setDraftDescription('');
    setSimilarTasks([]);
    setSearchTriggered(false);
    setSimilarSearchError(null);
    setIsCreateModalOpen(true);
  };

  const handleCreateTask = (values: CreateTaskFormValues) => {
    createTaskMutation.mutate({
      title: values.title,
      description: values.description || '',
      project_id: values.project_id,
      priority: values.priority || 'MEDIUM',
      type: values.type || 'feature',
      deadline: values.deadline?.format('YYYY-MM-DD'),
      status: TaskStatus.TODO,
    });
  };

  if (isLoading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* 顶部导航与操作 */}
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <Breadcrumb
            items={[
              { title: <a onClick={() => navigate('/')}>工作台</a> },
              { title: '任务看板' },
            ]}
            style={{ marginBottom: 8 }}
          />
          <Title level={3} style={{ margin: 0 }}>任务看板</Title>
        </div>

        <Space>
          <Select
            placeholder="筛选项目"
            value={projectFilter}
            onChange={setProjectFilter}
            style={{ width: 200 }}
          >
            <Option value="ALL">全部项目</Option>
            {projectIds.map((id) => {
              const projectName = projectNameMap.get(id);
              return (
                <Option key={id} value={id}>
                  {projectName || `项目 ${id}`}
                </Option>
              );
            })}
          </Select>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={openCreateTaskModal}
            size="large"
            style={{ borderRadius: 8 }}
          >
            创建任务
          </Button>
        </Space>
      </div>

      {/* 拖拽上下文 */}
      <DragDropContext onDragEnd={onDragEnd}>
        <div style={{ display: 'flex', gap: '20px', alignItems: 'flex-start', overflowX: 'auto', paddingBottom: 16, flex: 1 }}>
          {KanbanColumns.map((col) => (
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
                            hoverable
                            onClick={() => handleTaskClick(task.id)}
                            style={{
                              marginBottom: '12px',
                              borderRadius: '8px',
                              boxShadow: snapshot.isDragging
                                ? '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
                                : '0 1px 3px rgba(0, 0, 0, 0.05)',
                              border: '1px solid #e2e8f0',
                              background: '#fff',
                              cursor: 'pointer',
                              ...provided.draggableProps.style,
                            }}
                            styles={{ body: { padding: '12px' } }}
                          >
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                              <span style={{ fontSize: 12, color: '#94a3b8', fontWeight: 500 }}>#{task.id}</span>
                              <PriorityTag priority={task.priority || 'Medium'} />
                            </div>
                            <div style={{ fontWeight: 600, color: '#1e293b', marginBottom: 12, lineHeight: 1.5 }}>
                              {task.title}
                            </div>
                            <div
                              style={{ fontSize: 12, color: '#6366f1', cursor: 'pointer' }}
                              onClick={(e) => handleProjectClick(e, task.project_id)}
                            >
                              {projectNameMap.get(task.project_id) || `项目 ${task.project_id}`}
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

      <Modal
        title="创建任务"
        open={isCreateModalOpen}
        onOk={() => form.submit()}
        onCancel={() => {
          setIsCreateModalOpen(false);
          form.resetFields();
          setDraftTitle('');
          setDraftDescription('');
          setSimilarTasks([]);
          setSearchTriggered(false);
          setSimilarSearchError(null);
        }}
        confirmLoading={createTaskMutation.isPending}
        okText="创建"
        cancelText="取消"
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateTask}
          initialValues={{ type: 'feature', priority: 'MEDIUM' }}
          onValuesChange={(_, values) => {
            setDraftTitle(values.title || '');
            setDraftDescription(values.description || '');
          }}
        >
          <Form.Item
            name="title"
            label="任务标题"
            rules={[{ required: true, message: '请输入任务标题' }]}
          >
            <Input placeholder="例如：实现登录接口" />
          </Form.Item>

          <Form.Item
            name="project_id"
            label="所属项目"
            rules={[{ required: true, message: '请选择所属项目' }]}
          >
            <Select placeholder="选择项目">
              {projects.map((project: Project) => (
                <Option key={project.id} value={project.id}>
                  {project.name}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="type"
            label="任务类型"
            rules={[{ required: true, message: '请选择任务类型' }]}
          >
            <Select>
              <Option value="feature">新功能 (feature)</Option>
              <Option value="bug">Bug 修复 (bug)</Option>
              <Option value="docs">文档更新 (docs)</Option>
              <Option value="fix">修复 (fix)</Option>
              <Option value="chore">构建 (chore)</Option>
              <Option value="refactor">重构 (refactor)</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="priority"
            label="优先级"
            rules={[{ required: true, message: '请选择优先级' }]}
          >
            <Select>
              <Option value="HIGH">高</Option>
              <Option value="MEDIUM">中</Option>
              <Option value="LOW">低</Option>
            </Select>
          </Form.Item>

          <Form.Item name="deadline" label="截止日期">
            <DatePicker
              style={{ width: '100%' }}
              disabledDate={(current) => current && current < dayjs().startOf('day')}
            />
          </Form.Item>

          <Form.Item name="description" label="任务描述">
            <TextArea rows={4} placeholder="输入任务描述..." />
          </Form.Item>

          {isSearchingSimilar ? (
            <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginTop: 8 }}>
              <Spin size="small" />
              <span style={{ color: '#64748b' }}>正在进行语义查重...</span>
            </div>
          ) : searchTriggered && similarTasks.length > 0 ? (
            <Alert
              style={{ marginTop: 8 }}
              type="warning"
              showIcon
              message={`发现 ${similarTasks.length} 个相似任务，请确认是否重复`}
              description={(
                <List
                  size="small"
                  dataSource={similarTasks}
                  renderItem={(item) => (
                    <List.Item style={{ paddingInline: 0 }}>
                      <a onClick={() => navigate(`/tasks/${item.task_id}`)}>
                        #{item.task_id} {item.title}
                      </a>
                      <Tag color="orange">{Math.round(item.similarity * 100)}%</Tag>
                    </List.Item>
                  )}
                />
              )}
            />
          ) : similarSearchError ? (
            <Alert
              style={{ marginTop: 8 }}
              type="error"
              showIcon
              message={similarSearchError}
            />
          ) : searchTriggered ? (
            <Alert
              style={{ marginTop: 8 }}
              type="success"
              showIcon
              message="未发现明显重复任务"
            />
          ) : null}
        </Form>
      </Modal>
    </div>
  );
};
