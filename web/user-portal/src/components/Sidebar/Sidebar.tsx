import React from 'react';
import { Button, List, Typography, Popconfirm } from 'antd';
import {
  PlusOutlined,
  MessageOutlined,
  DeleteOutlined,
  RobotOutlined,
} from '@ant-design/icons';
import styles from './Sidebar.module.css';

const { Text } = Typography;

export interface Session {
  id: string;
  title: string;
  lastMessage?: string;
  timestamp: string;
}

interface SidebarProps {
  sessions: Session[];
  currentSessionId?: string;
  onNewSession: () => void;
  onSelectSession: (id: string) => void;
  onDeleteSession: (id: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  sessions,
  currentSessionId,
  onNewSession,
  onSelectSession,
  onDeleteSession,
}) => {
  // 格式化时间
  const formatTime = (time: string) => {
    const date = new Date(time);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) {
      return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
    } else if (days === 1) {
      return '昨天';
    } else if (days < 7) {
      const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
      return weekdays[date.getDay()];
    } else {
      return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
    }
  };

  return (
    <div className={styles.sidebar}>
      <div className={styles.header}>
        <div className={styles.logo}>
          <RobotOutlined className={styles.logoIcon} />
          <span className={styles.logoText}>SmartSupport</span>
        </div>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={onNewSession}
          block
        >
          新对话
        </Button>
      </div>

      <div className={styles.sessionList}>
        <Text type="secondary" className={styles.listTitle}>
          会话历史
        </Text>
        <List
          dataSource={sessions}
          renderItem={(session) => (
            <List.Item
              className={`${styles.sessionItem} ${
                session.id === currentSessionId ? styles.active : ''
              }`}
              onClick={() => onSelectSession(session.id)}
              actions={[
                <Popconfirm
                  title="确定删除这个会话吗？"
                  onConfirm={(e) => {
                    e?.stopPropagation();
                    onDeleteSession(session.id);
                  }}
                  okText="确定"
                  cancelText="取消"
                >
                  <DeleteOutlined
                    className={styles.deleteIcon}
                    onClick={(e) => e.stopPropagation()}
                  />
                </Popconfirm>,
              ]}
            >
              <List.Item.Meta
                avatar={<MessageOutlined className={styles.messageIcon} />}
                title={
                  <Text ellipsis className={styles.sessionTitle}>
                    {session.title || '新对话'}
                  </Text>
                }
                description={
                  <div className={styles.sessionMeta}>
                    <Text type="secondary" className={styles.time}>
                      {formatTime(session.timestamp)}
                    </Text>
                  </div>
                }
              />
            </List.Item>
          )}
        />
      </div>
    </div>
  );
};

export default Sidebar;
