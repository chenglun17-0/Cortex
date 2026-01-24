import React, { useState } from 'react';
import { Typography, Button, Card, List, Modal, Form, Input, message, Empty, Space, Popconfirm } from 'antd';
import { PlusOutlined, FolderOpenOutlined, RightOutlined, EditOutlined, DeleteOutlined, UserOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getProjects, createProject, updateProject, deleteProject } from './service';
import type { ProjectCreate, ProjectUpdate } from '../../types';
import { useNavigate } from 'react-router-dom';

const { Title, Paragraph, Text } = Typography;

export const ProjectsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingProject, setEditingProject] = useState<{ id: number; name: string; description?: string } | null>(null);
  const [form] = Form.useForm();
  const navigate = useNavigate();

  const { data: projects, isLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: getProjects,
  });

  const createMutation = useMutation({
    mutationFn: createProject,
    onSuccess: () => {
      message.success('项目创建成功！');
      setIsModalOpen(false);
      form.resetFields();
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
    onError: () => {
      message.error('创建失败，请重试');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: ProjectUpdate }) => updateProject(id, data),
    onSuccess: () => {
      message.success('项目更新成功！');
      setIsModalOpen(false);
      setEditingProject(null);
      form.resetFields();
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
    onError: () => {
      message.error('更新失败，请重试');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteProject,
    onSuccess: () => {
      message.success('项目已删除');
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '删除失败，请先删除项目下的任务');
    },
  });

  const handleCreate = (values: ProjectCreate) => {
    createMutation.mutate(values);
  };

  const handleUpdate = (values: ProjectUpdate) => {
    if (editingProject) {
      updateMutation.mutate({ id: editingProject.id, data: values });
    }
  };

  const openEditModal = (project: { id: number; name: string; description?: string }) => {
    setEditingProject(project);
    form.setFieldsValue({ name: project.name, description: project.description });
    setIsModalOpen(true);
  };

  const openCreateModal = () => {
    setEditingProject(null);
    form.resetFields();
    setIsModalOpen(true);
  };

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto' }}>
      {/* 顶部标题栏 */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 32 }}>
        <div>
          <Title level={2} style={{ margin: 0 }}>我的项目</Title>
          <Text type="secondary">管理和跟踪您的所有项目进度</Text>
        </div>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          size="large"
          onClick={openCreateModal}
          style={{ borderRadius: 8, height: 40 }}
        >
          创建新项目
        </Button>
      </div>

      {/* 项目列表展示 */}
      <List
        grid={{ gutter: 24, xs: 1, sm: 2, md: 3, lg: 3, xl: 4, xxl: 4 }}
        dataSource={projects}
        loading={isLoading}
        locale={{ emptyText: <Empty description="暂无项目，快去创建一个吧" style={{ marginTop: 64 }} /> }}
        renderItem={(item) => (
          <List.Item>
            <Card
              hoverable
              style={{
                borderRadius: 12,
                border: '1px solid #e2e8f0',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                height: '100%',
                display: 'flex',
                flexDirection: 'column'
              }}
              styles={{ body: { padding: 24, flex: 1, display: 'flex', flexDirection: 'column' } }}
              onClick={() => navigate(`/projects/${item.id}`)}
            >
              <div style={{ marginBottom: 16, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{
                  width: 40,
                  height: 40,
                  background: '#eff6ff',
                  borderRadius: 10,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <FolderOpenOutlined style={{ fontSize: 20, color: '#3b82f6' }} />
                </div>
                <Space>
                  <span style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    padding: '2px 8px',
                    background: '#eff6ff',
                    borderRadius: 6,
                    fontSize: 12,
                    color: '#3b82f6',
                    fontWeight: 500,
                  }}>
                    Active
                  </span>
                  <Space size={4}>
                    <Button
                      type="text"
                      icon={<EditOutlined />}
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        openEditModal(item);
                      }}
                    />
                    <Popconfirm
                      title="确定要删除此项目吗？"
                      description="删除前请确保项目下没有未完成的任务"
                      onConfirm={(e) => {
                        e?.stopPropagation();
                        deleteMutation.mutate(item.id);
                      }}
                      onCancel={(e) => e?.stopPropagation()}
                      okButtonProps={{ danger: true }}
                    >
                      <Button
                        type="text"
                        danger
                        icon={<DeleteOutlined />}
                        size="small"
                        onClick={(e) => e.stopPropagation()}
                      />
                    </Popconfirm>
                  </Space>
                </Space>
              </div>

              <Title level={4} style={{ margin: '0 0 8px 0', fontSize: 18 }}>{item.name}</Title>
              <Paragraph
                type="secondary"
                ellipsis={{ rows: 2 }}
                style={{ marginBottom: 24, flex: 1 }}
              >
                {item.description || '暂无项目描述，点击查看详情...'}
              </Paragraph>

              <div style={{
                borderTop: '1px solid #f1f5f9',
                paddingTop: 16,
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <Space size={4} style={{ color: '#6366f1', fontWeight: 500, fontSize: 13 }}>
                  <UserOutlined /> {item.members?.length || 0} 成员
                </Space>
                <Space size={4} style={{ color: '#6366f1', fontWeight: 500, fontSize: 13 }}>
                  进入看板 <RightOutlined style={{ fontSize: 10 }} />
                </Space>
              </div>
            </Card>
          </List.Item>
        )}
      />

      {/* 创建/编辑项目弹窗 */}
      <Modal
        title={editingProject ? '编辑项目' : '创建新项目'}
        open={isModalOpen}
        onOk={() => form.submit()}
        onCancel={() => {
          setIsModalOpen(false);
          setEditingProject(null);
          form.resetFields();
        }}
        confirmLoading={createMutation.isPending || updateMutation.isPending}
        okButtonProps={{ style: { borderRadius: 6 } }}
        cancelButtonProps={{ style: { borderRadius: 6 } }}
      >
        <Form form={form} layout="vertical" onFinish={editingProject ? handleUpdate : handleCreate}>
          <Form.Item
            name="name"
            label="项目名称"
            rules={[{ required: true, message: '请输入项目名称' }]}
          >
            <Input placeholder="例如：Cortex 研发系统" style={{ borderRadius: 6 }} />
          </Form.Item>
          <Form.Item name="description" label="项目描述">
            <Input.TextArea rows={3} placeholder="简要描述项目的目标..." style={{ borderRadius: 6 }} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};