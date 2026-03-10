import React, { useState, useRef, type KeyboardEvent } from 'react';
import { Input, Button } from 'antd';
import { SendOutlined } from '@ant-design/icons';
import styles from './ChatInput.module.css';

const { TextArea } = Input;

interface ChatInputProps {
  onSend: (message: string) => void;
  loading?: boolean;
  disabled?: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({ onSend, loading, disabled }) => {
  const [message, setMessage] = useState('');
  const inputRef = useRef<any>(null);

  const handleSend = () => {
    const trimmedMessage = message.trim();
    if (!trimmedMessage || loading || disabled) return;

    onSend(trimmedMessage);
    setMessage('');

    // 重置输入框高度
    if (inputRef.current) {
      inputRef.current.resizableTextArea.textArea.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className={styles.chatInput}>
      <div className={styles.inputWrapper}>
        <TextArea
          ref={inputRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="请输入您的问题...（Shift+Enter换行）"
          autoSize={{ minRows: 1, maxRows: 4 }}
          disabled={disabled || loading}
          className={styles.textArea}
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={handleSend}
          loading={loading}
          disabled={!message.trim() || disabled}
          className={styles.sendButton}
        >
          发送
        </Button>
      </div>
    </div>
  );
};

export default ChatInput;
