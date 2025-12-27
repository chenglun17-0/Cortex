import React, { useState } from 'react';
import { Form, Input, Button, Card, Typography, message, Layout } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { http } from '../../lib/http';


const { Title, Text } = Typography;
const { Content } = Layout;

export const LoginPage: React.FC = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);

    // 定义表单提交的数据类型
    const onFinish = async (values: any) => {
        setLoading (true);
        try {
            // 构造表单数据
            const formData = new FormData();
            //对应邮箱
            formData.append('username', values.username);
            formData.append('password', values.password);

            // 发送请求
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
        } finally {
            setLoading(false);
        }
    };
    return (
    <Layout style={{ minHeight: '100vh' }}>
      <Content style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#f0f2f5' }}>
        <Card style={{ width: 400, boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
          <div style={{ textAlign: 'center', marginBottom: 24 }}>
            <Title level={3} style={{ margin: 0 }}>Cortex</Title>
            <Text type="secondary">Cortex</Text>
          </div>

          <Form
            name="login_form"
            initialValues={{ remember: true }}
            onFinish={onFinish}
            size="large"
          >
            <Form.Item
              name="username"
              rules={[{ required: true, message: '请输入您的邮箱/用户名！' }]}
            >
              <Input 
                prefix={<UserOutlined />} 
                placeholder="邮箱 / 用户名" 
              />
            </Form.Item>

            <Form.Item
              name="password"
              rules={[{ required: true, message: '请输入密码！' }]}
            >
              <Input.Password 
                prefix={<LockOutlined />} 
                placeholder="密码" 
              />
            </Form.Item>

            <Form.Item>
              <Button type="primary" htmlType="submit" block loading={loading}>
                登录
              </Button>
            </Form.Item>
            
            <div style={{ textAlign: 'center' }}>
               <Text type="secondary" style={{ fontSize: '12px' }}>
                 还没有账号？请联系管理员
               </Text>
            </div>
          </Form>
        </Card>
      </Content>
    </Layout>
  );
};
