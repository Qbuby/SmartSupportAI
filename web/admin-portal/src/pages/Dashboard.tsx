import React from 'react';
import { Row, Col, Card, Statistic } from 'antd';
import { MessageOutlined, UserOutlined, FileTextOutlined } from '@ant-design/icons';

const Dashboard: React.FC = () => {
  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>仪表盘</h2>

      <Row gutter={16}>
        <Col span={8}>
          <Card>
            <Statistic
              title="今日对话"
              value={128}
              prefix={<MessageOutlined />}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="活跃用户"
              value={45}
              prefix={<UserOutlined />}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="知识库文档"
              value={23}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Card title="系统状态" style={{ marginTop: 24 }}>
        <p>向量数据库: <span style={{ color: 'green' }}>正常</span></p>
        <p>LLM服务: <span style={{ color: 'green' }}>正常</span></p>
        <p>API服务: <span style={{ color: 'green' }}>正常</span></p>
      </Card>
    </div>
  );
};

export default Dashboard;
