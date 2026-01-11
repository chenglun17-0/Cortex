import React, { useEffect } from 'react';
import { Form, Input, Button, message, Card, Row, Col, Typography } from 'antd';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getCurrentUser, updateProfile } from './service';
import type { UserUpdateProfile } from '../../types';

const { Title } = Typography;

export const ProfilePage: React.FC = () => {
  const queryClient = useQueryClient();
  const [form] = Form.useForm();
  const [passwordForm] = Form.useForm();

  const { data: currentUser, isLoading } = useQuery({
    queryKey: ['currentUser'],
    queryFn: getCurrentUser,
  });

  const { mutate: updateUser, isPending: isUpdating } = useMutation({
    mutationFn: (data: UserUpdateProfile) => updateProfile(data),
    onSuccess: (updatedUser) => {
      message.success('个人信息更新成功！');
      queryClient.setQueryData(['currentUser'], updatedUser);
      // Optional: Invalidate to refetch from server
      // queryClient.invalidateQueries({ queryKey: ['currentUser'] });
    },
    onError: (error) => {
      message.error(`更新失败: ${error.message}`);
    },
  });

  useEffect(() => {
    if (currentUser) {
      form.setFieldsValue({ username: currentUser.username });
    }
  }, [currentUser, form]);

  const onFinishUsername = (values: { username: string }) => {
    if (values.username !== currentUser?.username) {
      updateUser({ username: values.username });
    }
  };

  const onFinishPassword = (values: UserUpdateProfile) => {
    if (!values.old_password || !values.password) {
        message.error('请填写所有密码字段');
        return;
    }
    updateUser(values);
    passwordForm.resetFields();
  };

  if (isLoading) {
    return <div>加载中...</div>;
  }

  return (
    <Row gutter={[24, 24]}>
      <Col xs={24} md={12}>
        <Card>
          <Title level={4}>修改用户名</Title>
          <Form
            form={form}
            layout="vertical"
            onFinish={onFinishUsername}
            initialValues={{ username: currentUser?.username }}
          >
            <Form.Item
              label="用户名"
              name="username"
              rules={[{ required: true, message: '请输入新的用户名!' }]}
            >
              <Input />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit" loading={isUpdating}>
                保存
              </Button>
            </Form.Item>
          </Form>
        </Card>
      </Col>
      <Col xs={24} md={12}>
        <Card>
          <Title level={4}>修改密码</Title>
          <Form form={passwordForm} layout="vertical" onFinish={onFinishPassword}>
            <Form.Item
              label="旧密码"
              name="old_password"
              rules={[{ required: true, message: '请输入您的旧密码!' }]}
            >
              <Input.Password />
            </Form.Item>
            <Form.Item
              label="新密码"
              name="password"
              rules={[{ required: true, message: '请输入您的新密码!' }]}
            >
              <Input.Password />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit" loading={isUpdating}>
                修改密码
              </Button>
            </Form.Item>
          </Form>
        </Card>
      </Col>
    </Row>
  );
};
