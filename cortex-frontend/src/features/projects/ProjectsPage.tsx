import React, { useState } from 'react';
import { Layout, Typography, Button, Card, List, Modal, Form, Input, message, Empty } from 'antd';
import { PlusOutlined, FolderOpenOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getProjects, createProject } from './service';
import type { ProjectCreate } from '../../types';
import { useNavigate } from 'react-router-dom';

const { Content } = Layout;
const { Title, Paragraph } = Typography;

export const ProjectsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form] = Form.useForm();
  const navigate = useNavigate();
  // 1. 获取项目列表数据
  const { data: projects, isLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: getProjects,
  });

  // 2. 创建项目的 Mutation (变更操作)
  const createMutation = useMutation({
    mutationFn: createProject,
    onSuccess: () => {
      message.success('项目创建成功！');
      setIsModalOpen(false);
      form.resetFields();
      // 自动刷新列表，无需手动重新请求
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
    onError: () => {
      message.error('创建失败，请重试');
    },
  });

  const handleCreate = (values: ProjectCreate) => {
    createMutation.mutate(values);
  };

  return (
    <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      <Content style={{ padding: '40px' }}>
        {/* 顶部标题栏 */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
          <Title level={2} style={{ margin: 0 }}>我的项目</Title>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            size="large"
            onClick={() => setIsModalOpen(true)}
          >
            创建新项目
          </Button>
        </div>

        {/* 项目列表展示 */}
        <List
          grid={{ gutter: 16, xs: 1, sm: 2, md: 3, lg: 4, xl: 4, xxl: 6 }}
          dataSource={projects}
          loading={isLoading}
          locale={{ emptyText: <Empty description="暂无项目，快去创建一个吧" /> }}
          renderItem={(item) => (
            <List.Item>
              <Card
                hoverable
                style={{ cursor: 'pointer' }} // 1. 让鼠标悬停时变成"手型"
                onClick={() => navigate(`/projects/${item.id}`)} // 2. 点击整个卡片触发跳转
                title={item.name}
                extra={<FolderOpenOutlined style={{ color: '#1890ff' }} />}
              >
                <Paragraph ellipsis={{ rows: 2 }}>
                  {item.description || '暂无描述'}
                </Paragraph>
              </Card>
            </List.Item>
          )}
        />

        {/* 创建项目弹窗 */}
        <Modal
          title="创建新项目"
          open={isModalOpen}
          onOk={() => form.submit()}
          onCancel={() => setIsModalOpen(false)}
          confirmLoading={createMutation.isPending}
        >
          <Form form={form} layout="vertical" onFinish={handleCreate}>
            <Form.Item
              name="name"
              label="项目名称"
              rules={[{ required: true, message: '请输入项目名称' }]}
            >
              <Input placeholder="例如：Cortex 研发系统" />
            </Form.Item>
            <Form.Item name="description" label="描述">
              <Input.TextArea rows={3} placeholder="简要描述项目的目标..." />
            </Form.Item>
          </Form>
        </Modal>
      </Content>
    </Layout>
  );
};