import { useState, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Typography,
  Card,
  Descriptions,
  Tag,
  Button,
  Space,
  Breadcrumb,
  message,
  Modal,
  Form,
  Input,
  Select,
  Spin,
  Alert,
} from 'antd';
import {
  EditOutlined,
  BorderlessTableOutlined,
  SaveOutlined,
  CloseOutlined,
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getTaskById, updateTask } from './service';
import { getProjects } from '../projects/service';
import type { Project } from '../../types';
import { TaskStatus } from '../../types';
import { getStatusConfig, getPriorityConfig, formatDateTime } from '../../utils';

const { Title, Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;

export const TaskDetailPage: React.FC = () => {
  const { taskId } = useParams<{ taskId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [isEditing, setIsEditing] = useState(false);
  const [form] = Form.useForm();

  const { data: task, isLoading, error } = useQuery({
    queryKey: ['task', taskId],
    queryFn: () => getTaskById(taskId!),
    enabled: !!taskId,
  });

  const { data: projects = [] } = useQuery({
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

  // 获取当前任务的项目名称
  const projectName = task?.project_id ? projectNameMap.get(task.project_id) : undefined;

  const updateMutation = useMutation({
    mutationFn: (data: { title?: string; description?: string; status?: TaskStatus; priority?: string }) =>
      updateTask(Number(taskId), data),
    onSuccess: () => {
      message.success('任务更新成功');
      setIsEditing(false);
      queryClient.invalidateQueries({ queryKey: ['task', taskId] });
      queryClient.invalidateQueries({ queryKey: ['myTasks'] });
    },
    onError: () => {
      message.error('任务更新失败');
    },
  });

  const handleEdit = () => {
    form.setFieldsValue({
      title: task?.title,
      description: task?.description,
      status: task?.status,
      priority: task?.priority || 'MEDIUM',
    });
    setIsEditing(true);
  };

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      updateMutation.mutate(values);
    } catch (error) {
      message.error('请检查表单填写');
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
    form.resetFields();
  };

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
        <Spin size="large" />
      </div>
    );
  }

  if (error || !task) {
    return (
      <Alert
        message="任务不存在"
        description="无法找到该任务，可能已被删除或您没有访问权限。"
        type="error"
        showIcon
        action={
          <Button type="primary" onClick={() => navigate('/tasks')}>
            返回任务列表
          </Button>
        }
      />
    );
  }

  const statusInfo = getStatusConfig(task.status);
  const priorityInfo = getPriorityConfig(task.priority);

  return (
    <div>
      {/* 面包屑导航 */}
      <Breadcrumb
        items={[
          { title: <a onClick={() => navigate('/')}>工作台</a> },
          { title: <a onClick={() => navigate('/tasks')}>我的任务</a> },
          { title: task.title },
        ]}
        style={{ marginBottom: 16 }}
      />

      {/* 编辑表单模态框 */}
      <Modal
        title="编辑任务"
        open={isEditing}
        onOk={handleSave}
        onCancel={handleCancel}
        confirmLoading={updateMutation.isPending}
        okText="保存"
        cancelText="取消"
        okButtonProps={{ icon: <SaveOutlined /> }}
        cancelButtonProps={{ icon: <CloseOutlined /> }}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="title"
            label="任务标题"
            rules={[{ required: true, message: '请输入任务标题' }]}
          >
            <Input placeholder="例如：实现登录接口" />
          </Form.Item>

          <Form.Item name="status" label="状态" rules={[{ required: true }]}>
            <Select>
              <Option value={TaskStatus.TODO}>待处理</Option>
              <Option value={TaskStatus.IN_PROGRESS}>进行中</Option>
              <Option value={TaskStatus.REVIEW}>待审核</Option>
              <Option value={TaskStatus.DONE}>已完成</Option>
            </Select>
          </Form.Item>

          <Form.Item name="priority" label="优先级" rules={[{ required: true }]}>
            <Select>
              <Option value="HIGH">高</Option>
              <Option value="MEDIUM">中</Option>
              <Option value="LOW">低</Option>
            </Select>
          </Form.Item>

          <Form.Item name="description" label="详细描述">
            <TextArea rows={6} placeholder="输入任务描述..." />
          </Form.Item>
        </Form>
      </Modal>

      {/* 任务标题与操作 */}
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ flex: 1 }}>
          <Space size="middle" style={{ marginBottom: 8 }}>
            <Text type="secondary" style={{ fontSize: 14 }}>#{task.id}</Text>
            <Tag color={statusInfo.color}>{statusInfo.text}</Tag>
            <Tag color={priorityInfo.color}>{priorityInfo.text}优先级</Tag>
          </Space>
          <Title level={3} style={{ margin: 0 }}>{task.title}</Title>
        </div>
        <Space>
          <Button
            icon={<EditOutlined />}
            onClick={handleEdit}
            type="default"
          >
            编辑
          </Button>
          <Button
            icon={<BorderlessTableOutlined />}
            onClick={() => navigate(`/projects/${task.project_id}`)}
          >
            查看看板
          </Button>
        </Space>
      </div>

      {/* 任务详情 */}
      <Card>
        <Descriptions column={2} bordered>
          <Descriptions.Item label="任务ID">{task.id}</Descriptions.Item>
          <Descriptions.Item label="所属项目">
            <a onClick={() => navigate(`/projects/${task.project_id}`)}>
              {projectName || `项目 ${task.project_id}`}
            </a>
          </Descriptions.Item>
          <Descriptions.Item label="状态">
            <Tag color={statusInfo.color}>{statusInfo.text}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="优先级">
            <Tag color={priorityInfo.color}>{priorityInfo.text}</Tag>
          </Descriptions.Item>
          {task.branch_name && (
            <Descriptions.Item label="Git 分支" span={2}>
              <Text code>{task.branch_name}</Text>
            </Descriptions.Item>
          )}
          <Descriptions.Item label="创建时间" span={2}>
            {formatDateTime(task.created_at)}
          </Descriptions.Item>
          <Descriptions.Item label="更新时间" span={2}>
            {formatDateTime(task.updated_at)}
          </Descriptions.Item>
          <Descriptions.Item label="任务描述" span={2}>
            <Text style={{ whiteSpace: 'pre-wrap' }}>
              {task.description || '暂无描述'}
            </Text>
          </Descriptions.Item>
        </Descriptions>
      </Card>
    </div>
  );
};
