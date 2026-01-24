import React, { useState } from 'react';
import { Form, Input, Button, Card, Typography, message, Layout } from 'antd';
import { UserOutlined, LockOutlined, RocketOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { http } from '../../lib/http';


const { Title, Text } = Typography;
const { Content } = Layout;

export const LoginPage: React.FC = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);

    const onFinish = async (values: any) => {
        setLoading (true);
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
    <Layout style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)' }}>
      <Content style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '20px' }}>
        <Card
          variant="borderless"
          style={{
            width: 400,
            borderRadius: 16,
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
          }}
        >
          <div style={{ textAlign: 'center', marginBottom: 32 }}>
            <div style={{ 
              width: 64, 
              height: 64, 
              background: '#6366f1', 
              borderRadius: 12, 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center', 
              margin: '0 auto 16px',
              boxShadow: '0 10px 15px -3px rgba(99, 102, 241, 0.4)'
            }}>
              <RocketOutlined style={{ fontSize: 32, color: '#fff' }} />
            </div>
            <Title level={2} style={{ margin: 0, color: '#1e293b' }}>Cortex</Title>
            <Text type="secondary">智能项目协作平台</Text>
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
                prefix={<UserOutlined style={{ color: '#94a3b8' }} />} 
                placeholder="邮箱 / 用户名" 
                style={{ borderRadius: 8 }}
              />
            </Form.Item>

            <Form.Item
              name="password"
              rules={[{ required: true, message: '请输入密码！' }]}
            >
              <Input.Password 
                prefix={<LockOutlined style={{ color: '#94a3b8' }} />} 
                placeholder="密码" 
                style={{ borderRadius: 8 }}
              />
            </Form.Item>

            <Form.Item style={{ marginTop: 8 }}>
              <Button 
                type="primary" 
                htmlType="submit" 
                block 
                loading={loading}
                style={{ 
                  height: 48, 
                  borderRadius: 8, 
                  fontSize: 16, 
                  fontWeight: 600,
                  background: '#6366f1',
                  boxShadow: '0 4px 6px -1px rgba(99, 102, 241, 0.2)'
                }}
              >
                进入系统
              </Button>
            </Form.Item>
            
            <div style={{ textAlign: 'center' }}>
               <Text type="secondary" style={{ fontSize: '14px' }}>
                 还没有账号？请联系系统管理员
               </Text>
            </div>
          </Form>
        </Card>
      </Content>
    </Layout>
  );
};
