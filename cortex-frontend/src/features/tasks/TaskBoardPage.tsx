import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Typography, Card, Spin, Tag, Select, Space, Breadcrumb } from 'antd';
import { DragDropContext, Droppable, Draggable, type DropResult } from '@hello-pangea/dnd';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getMyTasks, updateTask } from './service';
import { getProjects } from '../projects/service';
import type { Task } from '../../types';
import type { Project } from '../../types';
import { TaskStatus, KanbanColumns } from '../../constants';
import { getPriorityConfig } from '../../utils';

const { Title } = Typography;
const { Option } = Select;

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
  const [projectFilter, setProjectFilter] = useState<number | 'ALL'>('ALL');

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
    </div>
  );
};
