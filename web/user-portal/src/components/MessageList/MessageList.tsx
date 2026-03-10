import React, { useRef, useEffect } from 'react';
import { Empty, Spin } from 'antd';
import MessageItem from '../MessageItem/MessageItem';
import styles from './MessageList.module.css';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
  contextCount?: number;
  toolUsed?: string;
}

interface MessageListProps {
  messages: Message[];
  loading?: boolean;
}

const MessageList: React.FC<MessageListProps> = ({ messages, loading }) => {
  const listRef = useRef<HTMLDivElement>(null);

  // 自动滚动到底部
  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className={styles.empty}>
        <Empty
          description="开始新的对话吧"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      </div>
    );
  }

  return (
    <div ref={listRef} className={styles.messageList}>
      {messages.map((message) => (
        <MessageItem
          key={message.id}
          role={message.role}
          content={message.content}
          timestamp={message.timestamp}
          contextCount={message.contextCount}
          toolUsed={message.toolUsed}
        />
      ))}
      {loading && (
        <div className={styles.loading}>
          <Spin tip="思考中..." />
        </div>
      )}
    </div>
  );
};

export default MessageList;
