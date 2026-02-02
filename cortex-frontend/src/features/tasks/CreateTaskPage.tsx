import React, { useState, useEffect, useCallback } from 'react';
import {
  Typography, Button, Form, Input, Select, DatePicker, Card,
  List, message, Space, Spin, Alert, Divider
} from 'antd';
import {
  PlusOutlined, WarningOutlined, LinkOutlined, FileTextOutlined
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { searchSimilarTasks } from './similarityService';
import type { SimilarTask } from './similarityService';
import { getProjects } from '../projects/service';
import { createTask } from './service';
import type { TaskCreate } from '../../types';
import dayjs from 'dayjs';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

export const CreateTaskPage: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [form] = Form.useForm();

  // 表单状态
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [similarTasks, setSimilarTasks] = useState<SimilarTask[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchTriggered, setSearchTriggered] = useState(false);

  // 获取项目列表
  const { data: projects } = useQuery({
    queryKey: ['projects'],
    queryFn: getProjects,
  });

  // 创建任务 mutation
  const createMutation = useMutation({
    mutationFn: (data: TaskCreate) => createTask(data),
    onSuccess: (newTask) => {
      message.success('任务创建成功！');
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      // 跳转到任务详情页
      navigate(`/tasks/${newTask.id}`);
    },
    onError: () => {
      message.error('创建失败，请重试');
    },
  });

  // 搜索相似任务（防抖）
  const searchSimilar = useCallback(async () => {
    if (!title.trim() || title.length < 3) {
      setSimilarTasks([]);
      setSearchTriggered(false);
      return;
    }

    setIsSearching(true);
    setSearchTriggered(true);

    try {
      const textContent = `${title}\n${description || ''}`;
      const response = await searchSimilarTasks({
        text: textContent,
        limit: 5,
        threshold: 0.3,
      });

      if (response.success) {
        setSimilarTasks(response.results);
      } else {
        setSimilarTasks([]);
      }
    } catch (error) {
      console.error('搜索相似任务失败:', error);
      setSimilarTasks([]);
    } finally {
      setIsSearching(false);
    }
  }, [title, description]);

  // 防抖搜索（标题变化后 500ms 自动搜索）
  useEffect(() => {
    const timer = setTimeout(() => {
      searchSimilar();
    }, 500);

    return () => clearTimeout(timer);
  }, [title, description, searchSimilar]);

  // 手动触发搜索
  const handleManualSearch = () => {
    searchSimilar();
  };

  const handleSubmit = (values: any) => {
    const taskData: TaskCreate = {
      title: values.title,
      description: values.description || '',
      project_id: values.project_id,
      priority: values.priority || 'MEDIUM',
      deadline: values.deadline?.format('YYYY-MM-DD'),
      type: values.type || 'feature',
      status: 'TODO',
    };

    createMutation.mutate(taskData);
  };

  // 获取优先级颜色
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'HIGH': return 'red';
      case 'MEDIUM': return 'orange';
      case 'LOW': return 'green';
      default: return 'default';
    }
  };

  // 获取状态颜色
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'TODO': return 'default';
      case 'IN_PROGRESS': return 'processing';
      case 'REVIEW': return 'warning';
      case 'DONE': return 'success';
      default: return 'default';
    }
  };

  return (
    <div style={{ maxWidth: 1000, margin: '0 auto' }}>
      {/* 页面标题 */}
      <div style={{ marginBottom: 32 }}>
        <Title level={2} style={{ margin: 0 }}>创建任务</Title>
        <Text type="secondary">填写任务信息，AI 将自动检测是否存在相似任务</Text>
      </div>

      <div style={{ display: 'flex', gap: 24 }}>
        {/* 左侧：创建表单 */}
        <div style={{ flex: 1 }}>
          <Card
            style={{
              borderRadius: 12,
              border: '1px solid #e2e8f0',
              marginBottom: 24
            }}
            styles={{ body: { padding: 24 } }}
          >
            <Form
              form={form}
              layout="vertical"
              onFinish={handleSubmit}
              initialValues={{ type: 'feature', priority: 'MEDIUM' }}
            >
              <Form.Item
                name="title"
                label="任务标题"
                rules={[
                  { required: true, message: '请输入任务标题' },
                  { min: 3, message: '标题至少需要 3 个字符' }
                ]}
              >
                <Input
                  placeholder="简要描述任务目标..."
                  size="large"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  style={{ borderRadius: 8 }}
                />
              </Form.Item>

              <Form.Item
                name="description"
                label="任务描述"
              >
                <TextArea
                  rows={4}
                  placeholder="详细描述任务内容、背景和验收标准..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  style={{ borderRadius: 8 }}
                />
              </Form.Item>

              <div style={{ display: 'flex', gap: 16 }}>
                <Form.Item
                  name="project_id"
                  label="所属项目"
                  rules={[{ required: true, message: '请选择项目' }]}
                  style={{ flex: 1 }}
                >
                  <Select
                    placeholder="选择所属项目"
                    style={{ borderRadius: 8 }}
                    options={projects?.map(p => ({
                      label: p.name,
                      value: p.id
                    }))}
                  />
                </Form.Item>

                <Form.Item
                  name="type"
                  label="任务类型"
                  style={{ width: 140 }}
                >
                  <Select
                    options={[
                      { label: '功能开发', value: 'feature' },
                      { label: 'Bug 修复', value: 'bug' },
                      { label: '文档更新', value: 'docs' },
                      { label: '代码优化', value: 'refactor' },
                    ]}
                  />
                </Form.Item>

                <Form.Item
                  name="priority"
                  label="优先级"
                  style={{ width: 120 }}
                >
                  <Select
                    options={[
                      { label: '高', value: 'HIGH', style: { color: '#ef4444' } },
                      { label: '中', value: 'MEDIUM', style: { color: '#f97316' } },
                      { label: '低', value: 'LOW', style: { color: '#22c55e' } },
                    ]}
                  />
                </Form.Item>
              </div>

              <Form.Item
                name="deadline"
                label="截止日期"
              >
                <DatePicker
                  style={{ width: '100%', borderRadius: 8 }}
                  disabledDate={(current) => current && current < dayjs().startOf('day')}
                />
              </Form.Item>

              <Form.Item style={{ marginBottom: 0, marginTop: 24 }}>
                <Space size={16}>
                  <Button
                    type="primary"
                    htmlType="submit"
                    size="large"
                    loading={createMutation.isPending}
                    style={{ borderRadius: 8, height: 44 }}
                  >
                    创建任务
                  </Button>
                  <Button
                    size="large"
                    onClick={() => navigate(-1)}
                    style={{ borderRadius: 8, height: 44 }}
                  >
                    取消
                  </Button>
                </Space>
              </Form.Item>
            </Form>
          </Card>
        </div>

        {/* 右侧：相似任务推荐 */}
        <div style={{ width: 340 }}>
          <Card
            style={{
              borderRadius: 12,
              border: '1px solid #e2e8f0',
              position: 'sticky',
              top: 24
            }}
            styles={{ body: { padding: 20 } }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
              <FileTextOutlined style={{ fontSize: 18, color: '#6366f1' }} />
              <Title level={5} style={{ margin: 0 }}>相似任务检测</Title>
            </div>

            {/* 搜索状态 */}
            {isSearching ? (
              <div style={{ textAlign: 'center', padding: '20px 0' }}>
                <Spin size="small" />
                <Text type="secondary" style={{ marginLeft: 8 }}>正在分析...</Text>
              </div>
            ) : title.length < 3 ? (
              <Alert
                type="info"
                message="输入任务标题"
                description="输入至少 3 个字符后将自动检测相似任务"
                showIcon
                style={{ borderRadius: 8 }}
              />
            ) : searchTriggered && similarTasks.length === 0 ? (
              <Alert
                type="success"
                message="未发现相似任务"
                description="当前任务描述与历史任务差异较大，可以继续创建"
                showIcon
                style={{ borderRadius: 8 }}
              />
            ) : searchTriggered && similarTasks.length > 0 ? (
              <>
                <Alert
                  type="warning"
                  message={`发现 ${similarTasks.length} 个相似任务`}
                  description="请确认您要创建的任务是否与以下任务重复"
                  showIcon
                  style={{ marginBottom: 16, borderRadius: 8 }}
                />

                <List
                  size="small"
                  dataSource={similarTasks}
                  renderItem={(item) => (
                    <List.Item style={{ padding: '12px 0', borderBottom: '1px solid #f1f5f9' }}>
                      <div style={{ width: '100%' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 4 }}>
                          <Text strong style={{ fontSize: 13, flex: 1 }}>
                            {item.title}
                          </Text>
                          <span style={{
                            padding: '2px 6px',
                            background: '#fef3c7',
                            borderRadius: 4,
                            fontSize: 11,
                            color: '#d97706',
                            fontWeight: 500,
                            marginLeft: 8
                          }}>
                            {(item.similarity * 100).toFixed(0)}%
                          </span>
                        </div>
                        <div style={{ display: 'flex', gap: 8, marginBottom: 4 }}>
                          <span style={{
                            padding: '2px 6px',
                            background: '#f1f5f9',
                            borderRadius: 4,
                            fontSize: 11,
                            color: '#64748b'
                          }}>
                            {item.status}
                          </span>
                          <span style={{
                            padding: '2px 6px',
                            background: item.priority === 'HIGH' ? '#fef2f2' : item.priority === 'MEDIUM' ? '#fff7ed' : '#f0fdf4',
                            borderRadius: 4,
                            fontSize: 11,
                            color: getPriorityColor(item.priority)
                          }}>
                            {item.priority}
                          </span>
                        </div>
                        <Button
                          type="link"
                          size="small"
                          icon={<LinkOutlined />}
                          onClick={() => navigate(`/tasks/${item.task_id}`)}
                          style={{ padding: 0, fontSize: 12 }}
                        >
                          查看详情
                        </Button>
                      </div>
                    </List.Item>
                  )}
                />

                <Divider style={{ margin: '12px 0' }} />

                <Text type="secondary" style={{ fontSize: 12 }}>
                  <WarningOutlined style={{ marginRight: 4 }} />
                  如果上述任务与您要创建的内容重复，请直接处理已有任务，避免重复造轮子
                </Text>
              </>
            ) : null}
          </Card>
        </div>
      </div>
    </div>
  );
};
