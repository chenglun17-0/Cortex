import React, { useState } from 'react';
import { Form, Input, Button, Card, Typography, message } from 'antd';
import { UserOutlined, LockOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { http } from '../../lib/http';
import './LoginPage.css';


const { Title, Text } = Typography;

export const LoginPage: React.FC = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);

    const onFinish = async (values: { username: string; password: string }) => {
        setLoading(true);
        try {
            const formData = new FormData();
            formData.append('username', values.username);
            formData.append('password', values.password);

            const response = await http.post('/login/access-token', formData, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                }
            });
            const { access_token } = response.data;
            localStorage.setItem('access_token', access_token);

            message.success('登录成功！');
            navigate('/');
        } catch (error) {
            console.error('Login failed:', error);
            message.error('登录失败，请检查用户名或密码');
        } finally {
            setLoading(false);
        }
    };

    return (
    <div className="login-page">
      <div className="login-page__mesh" />
      <div className="login-page__blob login-page__blob--one" />
      <div className="login-page__blob login-page__blob--two" />

      <main className="login-page__content">
        <section className="login-brand">
          <div className="login-brand__badge">Project Intelligence Platform</div>
          <Title level={1} className="login-brand__title">Cortex</Title>
          <Text className="login-brand__desc">AI 驱动的项目协作与任务管理工作台</Text>
          <ul className="login-brand__list">
            <li><CheckCircleOutlined /> 统一任务看板与项目协同</li>
            <li><CheckCircleOutlined /> AI 语义查重与审查回写</li>
            <li><CheckCircleOutlined /> 清晰的成员权限与责任边界</li>
          </ul>
        </section>

        <Card variant="borderless" className="login-card">
          <div className="login-card__header">
            <Title level={2} className="login-card__title">欢迎登录</Title>
          </div>

          <Form
            name="login_form"
            initialValues={{ remember: true }}
            onFinish={onFinish}
            size="large"
            layout="vertical"
          >
            <Form.Item
              name="username"
              rules={[{ required: true, message: '请输入您的邮箱/用户名！' }]}
            >
              <Input
                prefix={<UserOutlined className="login-card__icon" />}
                placeholder="邮箱 / 用户名"
                className="login-card__input"
              />
            </Form.Item>

            <Form.Item
              name="password"
              rules={[{ required: true, message: '请输入密码！' }]}
            >
              <Input.Password
                prefix={<LockOutlined className="login-card__icon" />}
                placeholder="密码"
                className="login-card__input"
              />
            </Form.Item>

            <Form.Item style={{ marginTop: 8, marginBottom: 10 }}>
              <Button
                type="primary"
                htmlType="submit"
                block
                loading={loading}
                className="login-card__submit"
              >
                进入系统
              </Button>
            </Form.Item>

            <div className="login-card__footer">
               <Text>
                 还没有账号？请联系系统管理员
               </Text>
            </div>
          </Form>
        </Card>
      </main>
    </div>
  );
};
