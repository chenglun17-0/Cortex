import { Alert, Card, Col, Empty, Progress, Row, Statistic, Table, Tag, Typography } from 'antd';
import { BarChartOutlined, CheckCircleOutlined, ProjectOutlined, UnorderedListOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';

import { getOverviewReport } from './service';
import { getPriorityConfig, getStatusConfig } from '../../utils';

const { Title, Text } = Typography;

export const AnalyticsPage: React.FC = () => {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['analyticsOverview'],
    queryFn: getOverviewReport,
  });

  const statusColumns = [
    {
      title: '状态',
      dataIndex: 'key',
      key: 'key',
      render: (value: string) => {
        const config = getStatusConfig(value);
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
    {
      title: '任务数',
      dataIndex: 'count',
      key: 'count',
    },
  ];

  const priorityColumns = [
    {
      title: '优先级',
      dataIndex: 'key',
      key: 'key',
      render: (value: string) => {
        const config = getPriorityConfig(value);
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
    {
      title: '任务数',
      dataIndex: 'count',
      key: 'count',
    },
  ];

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto' }}>
      <div style={{ marginBottom: 24 }}>
        <Title level={2} style={{ marginBottom: 8 }}>
          数据报表
        </Title>
        <Text type="secondary">查看项目和任务的基础统计与完成情况。</Text>
      </div>

      {isError && (
        <Alert
          type="error"
          showIcon
          message="报表数据加载失败"
          description="请稍后重试，或检查后端服务是否正常。"
          style={{ marginBottom: 16 }}
        />
      )}

      <Row gutter={24} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card variant="borderless" loading={isLoading}>
            <Statistic
              title="参与项目数"
              value={data?.total_projects ?? 0}
              prefix={<ProjectOutlined style={{ color: '#3b82f6' }} />}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card variant="borderless" loading={isLoading}>
            <Statistic
              title="任务总数"
              value={data?.total_tasks ?? 0}
              prefix={<UnorderedListOutlined style={{ color: '#6366f1' }} />}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card variant="borderless" loading={isLoading}>
            <Statistic
              title="已完成任务"
              value={data?.completed_tasks ?? 0}
              prefix={<CheckCircleOutlined style={{ color: '#10b981' }} />}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={24}>
        <Col span={8}>
          <Card
            title={
              <span>
                <BarChartOutlined style={{ marginRight: 8 }} />
                完成率
              </span>
            }
            variant="borderless"
            loading={isLoading}
            style={{ minHeight: 300 }}
          >
            {data ? (
              <div style={{ paddingTop: 12 }}>
                <Progress
                  type="dashboard"
                  percent={Math.round(data.completion_rate)}
                  strokeColor={data.completion_rate >= 80 ? '#10b981' : '#3b82f6'}
                />
                <div style={{ textAlign: 'center', marginTop: 8 }}>
                  <Text type="secondary">{data.completed_tasks} / {data.total_tasks} 已完成</Text>
                </div>
              </div>
            ) : (
              <Empty description="暂无统计数据" />
            )}
          </Card>
        </Col>
        <Col span={8}>
          <Card title="按状态分布" variant="borderless" loading={isLoading} style={{ minHeight: 300 }}>
            <Table
              size="small"
              rowKey="key"
              pagination={false}
              dataSource={data?.status_distribution ?? []}
              columns={statusColumns}
              locale={{ emptyText: <Empty description="暂无数据" image={Empty.PRESENTED_IMAGE_SIMPLE} /> }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card title="按优先级分布" variant="borderless" loading={isLoading} style={{ minHeight: 300 }}>
            <Table
              size="small"
              rowKey="key"
              pagination={false}
              dataSource={data?.priority_distribution ?? []}
              columns={priorityColumns}
              locale={{ emptyText: <Empty description="暂无数据" image={Empty.PRESENTED_IMAGE_SIMPLE} /> }}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};
