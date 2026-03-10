import React from 'react';
import { Avatar, Typography } from 'antd';
import { UserOutlined, RobotOutlined, FileTextOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import styles from './MessageItem.module.css';

const { Text } = Typography;

interface MessageItemProps {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
  contextCount?: number;
  toolUsed?: string;
}

const MessageItem: React.FC<MessageItemProps> = ({
  role,
  content,
  timestamp,
  contextCount,
  toolUsed,
}) => {
  const isUser = role === 'user';

  // 格式化时间
  const formatTime = (time?: string) => {
    if (!time) return '';
    const date = new Date(time);
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className={`${styles.messageItem} ${isUser ? styles.userMessage : styles.assistantMessage}`}>
      <div className={styles.avatar}>
        <Avatar
          icon={isUser ? <UserOutlined /> : <RobotOutlined />}
          style={{
            backgroundColor: isUser ? '#1890ff' : '#52c41a',
          }}
        />
      </div>
      <div className={styles.content}>
        <div className={styles.bubble}>
          {isUser ? (
            <Text className={styles.text}>{content}</Text>
          ) : (
            <div className={styles.markdown}>
              <ReactMarkdown>{content}</ReactMarkdown>
            </div>
          )}
        </div>
        <div className={styles.meta}>
          {timestamp && (
            <Text type="secondary" className={styles.time}>
              {formatTime(timestamp)}
            </Text>
          )}
          {!isUser && contextCount !== undefined && contextCount > 0 && (
            <Text type="secondary" className={styles.context}>
              <FileTextOutlined /> 参考 {contextCount} 篇文档
            </Text>
          )}
          {!isUser && toolUsed && (
            <Text type="secondary" className={styles.tool}>
              使用工具: {toolUsed}
            </Text>
          )}
        </div>
      </div>
    </div>
  );
};

export default MessageItem;
