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
  List,
  Empty,
} from 'antd';
import {
  EditOutlined,
  BorderlessTableOutlined,
  SaveOutlined,
  CloseOutlined,
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getTaskById, updateTask, getTaskComments, createTaskComment } from './service';
import { getProjectMembers, getProjects } from '../projects/service';
import type { Project, TaskComment, TaskUpdate, User } from '../../types';
import { TaskStatus } from '../../types';
import { getStatusConfig, getPriorityConfig, formatDateTime } from '../../utils';

const { Title, Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;

const AI_REVIEW_HEADER = '## AI 代码审查结果';
const AI_REVIEW_SCORE_PATTERN = /\*\*评分\*\*:\s*(\d{1,3})\s*\/\s*100/;
const AI_REVIEW_SUMMARY_PATTERN = /\*\*摘要\*\*:\s*(.+)/;

interface ParsedAiReview {
  createdAt: string;
  score: number | null;
  summary: string;
}

const parseAiReviewComment = (comment: TaskComment): ParsedAiReview | null => {
  const content = comment.content || '';
  if (!content.includes(AI_REVIEW_HEADER)) {
    return null;
  }

  const scoreMatch = content.match(AI_REVIEW_SCORE_PATTERN);
  const score = scoreMatch ? Number(scoreMatch[1]) : null;
  const summaryMatch = content.match(AI_REVIEW_SUMMARY_PATTERN);

  return {
    createdAt: comment.created_at,
    score: Number.isFinite(score) ? score : null,
    summary: summaryMatch?.[1]?.trim() || '未提供摘要',
  };
};

const getAiReviewStatus = (score: number | null): { label: string; color: string } => {
  if (score === null) {
    return { label: '未知', color: 'default' };
  }
  if (score >= 90) {
    return { label: '优秀', color: 'success' };
  }
  if (score >= 75) {
    return { label: '良好', color: 'processing' };
  }
  return { label: '需关注', color: 'warning' };
};

export const TaskDetailPage: React.FC = () => {
  const { taskId } = useParams<{ taskId: string }>();
  const parsedTaskId = Number(taskId);
  const hasValidTaskId = Number.isInteger(parsedTaskId) && parsedTaskId > 0;
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [isEditing, setIsEditing] = useState(false);
  const [commentPage, setCommentPage] = useState(1);
  const [commentPageSize, setCommentPageSize] = useState(10);
  const [form] = Form.useForm();
  const [commentForm] = Form.useForm();

  const { data: task, isLoading, error, isSuccess: isTaskLoaded } = useQuery({
    queryKey: ['task', parsedTaskId],
    queryFn: () => getTaskById(parsedTaskId),
    enabled: hasValidTaskId,
  });

  const { data: projects = [] } = useQuery({
    queryKey: ['projects'],
    queryFn: getProjects,
  });

  const { data: projectMembers = [] } = useQuery({
    queryKey: ['projectMembers', task?.project_id],
    queryFn: () => getProjectMembers(task!.project_id),
    enabled: !!task?.project_id,
  });

  const {
    data: commentsData,
    isLoading: commentsLoading,
    isError: isCommentsLoadError,
    error: commentsError,
    isFetching: commentsFetching,
    refetch: refetchComments,
  } = useQuery({
    queryKey: ['task-comments', parsedTaskId, commentPage, commentPageSize],
    queryFn: () => getTaskComments(parsedTaskId, commentPage, commentPageSize),
    enabled: hasValidTaskId && isTaskLoaded,
  });
  const { data: aiReviewCommentsData } = useQuery({
    queryKey: ['task-ai-review-comments', parsedTaskId],
    queryFn: () => getTaskComments(parsedTaskId, 1, 50),
    enabled: hasValidTaskId && isTaskLoaded,
  });
  const latestAiReview = useMemo(() => {
    const parsedReviews = (aiReviewCommentsData?.items ?? [])
      .map(parseAiReviewComment)
      .filter((item): item is ParsedAiReview => item !== null);

    if (parsedReviews.length === 0) {
      return null;
    }

    return parsedReviews.sort(
      (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime(),
    )[0];
  }, [aiReviewCommentsData?.items]);
  const aiReviewStatus = getAiReviewStatus(latestAiReview?.score ?? null);
  const commentsErrorMessage =
    commentsError instanceof Error ? commentsError.message : '评论加载失败，请稍后重试';

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
  const memberMap = useMemo(() => {
    const map = new Map<number, User>();
    projectMembers.forEach((member) => map.set(member.id, member));
    return map;
  }, [projectMembers]);

  const assignee = task?.assignee_id ? memberMap.get(task.assignee_id) : undefined;
  const collaboratorUsers = (task?.collaborator_ids || [])
    .map((userId) => memberMap.get(userId))
    .filter((member): member is User => !!member);

  const updateMutation = useMutation({
    mutationFn: (data: TaskUpdate) => updateTask(parsedTaskId, data),
    onSuccess: () => {
      message.success('任务更新成功');
      setIsEditing(false);
      queryClient.invalidateQueries({ queryKey: ['task', parsedTaskId] });
      queryClient.invalidateQueries({ queryKey: ['myTasks'] });
    },
    onError: () => {
      message.error('任务更新失败');
    },
  });

  const createCommentMutation = useMutation({
    mutationFn: (content: string) => createTaskComment(parsedTaskId, content),
    onSuccess: () => {
      message.success('评论发布成功');
      commentForm.resetFields();
      setCommentPage(1);
      queryClient.invalidateQueries({ queryKey: ['task-comments', parsedTaskId] });
      queryClient.invalidateQueries({ queryKey: ['task-ai-review-comments', parsedTaskId] });
    },
    onError: () => {
      message.error('评论发布失败');
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
    } catch {
      message.error('请检查表单填写');
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
    form.resetFields();
  };

  const handleCommentSubmit = async () => {
    try {
      const values = await commentForm.validateFields();
      createCommentMutation.mutate(values.content.trim());
    } catch {
      message.error('请输入评论内容');
    }
  };

  if (!hasValidTaskId) {
    return (
      <Alert
        message="任务ID无效"
        description="请确认访问链接是否正确。"
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
          <Descriptions.Item label="负责人">
            {task.assignee_id ? (assignee ? `${assignee.username} (${assignee.email})` : `用户 #${task.assignee_id}`) : '未指定'}
          </Descriptions.Item>
          <Descriptions.Item label="协同人">
            {task.collaborator_ids.length > 0 ? (
              collaboratorUsers.length > 0 ? (
                <Space direction="vertical" size={4}>
                  {collaboratorUsers.map((member) => (
                    <Text key={member.id}>{member.username} ({member.email})</Text>
                  ))}
                </Space>
              ) : (
                task.collaborator_ids.map((userId) => (
                  <Text key={userId} style={{ display: 'block' }}>用户 #{userId}</Text>
                ))
              )
            ) : '无'}
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

      {/* 评论区 */}
      <Card title={`评论 (${commentsData?.total ?? 0})`} style={{ marginTop: 16 }}>
        <Card title="PR 审查状态" size="small" type="inner" style={{ marginBottom: 16 }}>
          {latestAiReview ? (
            <Descriptions size="small" column={1}>
              <Descriptions.Item label="状态">
                <Tag color={aiReviewStatus.color}>{aiReviewStatus.label}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="评分">
                {latestAiReview.score !== null ? `${latestAiReview.score}/100` : '未提供'}
              </Descriptions.Item>
              <Descriptions.Item label="摘要">
                <Text style={{ whiteSpace: 'pre-wrap' }}>{latestAiReview.summary}</Text>
              </Descriptions.Item>
              <Descriptions.Item label="更新时间">
                {formatDateTime(latestAiReview.createdAt)}
              </Descriptions.Item>
            </Descriptions>
          ) : (
            <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无审查结果" />
          )}
        </Card>

        <Form form={commentForm} layout="vertical">
          <Form.Item
            name="content"
            label="发表评论"
            rules={[
              { required: true, message: '请输入评论内容' },
              {
                validator: (_, value: string | undefined) =>
                  value && value.trim() ? Promise.resolve() : Promise.reject(new Error('请输入评论内容')),
              },
              { max: 2000, message: '评论内容不能超过 2000 字' },
            ]}
          >
            <TextArea rows={3} placeholder="输入评论内容..." />
          </Form.Item>
          <Form.Item style={{ marginBottom: 16 }}>
            <Button
              type="primary"
              onClick={handleCommentSubmit}
              loading={createCommentMutation.isPending}
            >
              发布评论
            </Button>
          </Form.Item>
        </Form>

        {commentsLoading ? (
          <Spin />
        ) : isCommentsLoadError ? (
          <Alert
            message="评论加载失败"
            description={commentsErrorMessage}
            type="error"
            showIcon
            action={
              <Button type="primary" size="small" loading={commentsFetching} onClick={refetchComments}>
                重试
              </Button>
            }
          />
        ) : !commentsData || commentsData.items.length === 0 ? (
          <Empty description="暂无评论" />
        ) : (
          <List
            dataSource={commentsData.items}
            itemLayout="horizontal"
            pagination={{
              current: commentPage,
              pageSize: commentPageSize,
              total: commentsData.total,
              showSizeChanger: true,
              pageSizeOptions: ['5', '10', '20'],
              hideOnSinglePage: true,
              onChange: (page, pageSize) => {
                setCommentPage(page);
                setCommentPageSize(pageSize);
              },
            }}
            renderItem={(comment: TaskComment) => (
              <List.Item>
                <List.Item.Meta
                  title={
                    <Space size={8}>
                      <Text strong>{comment.author?.username || `用户 ${comment.author_id}`}</Text>
                      <Text type="secondary">{formatDateTime(comment.created_at)}</Text>
                    </Space>
                  }
                  description={<Text style={{ whiteSpace: 'pre-wrap' }}>{comment.content}</Text>}
                />
              </List.Item>
            )}
          />
        )}
      </Card>
    </div>
  );
};
