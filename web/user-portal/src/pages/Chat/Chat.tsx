import React, { useState, useCallback, useEffect } from 'react';
import { message as antMessage } from 'antd';
import Sidebar, { type Session } from '../../components/Sidebar/Sidebar';
import MessageList, { type Message } from '../../components/MessageList/MessageList';
import ChatInput from '../../components/ChatInput/ChatInput';
import { chatApi } from '../../api/chat';
import styles from './Chat.module.css';

// 生成唯一ID
const generateId = () => Math.random().toString(36).substring(2, 9);

// 获取当前用户ID（实际项目中应从登录态获取）
const getUserId = () => {
  let userId = localStorage.getItem('smartsupport_user_id');
  if (!userId) {
    userId = `user_${generateId()}`;
    localStorage.setItem('smartsupport_user_id', userId);
  }
  return userId;
};

const Chat: React.FC = () => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string>();
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [userId] = useState(() => getUserId());

  // 加载会话列表
  const loadSessions = useCallback(async () => {
    try {
      const data = await chatApi.getSessions();
      const formattedSessions: Session[] = data.map((s) => ({
        id: s.session_id,
        title: `会话 ${s.session_id.slice(-6)}`,
        timestamp: s.last_active || s.created_at,
      }));
      setSessions(formattedSessions);
      return formattedSessions;
    } catch (error) {
      console.error('加载会话失败:', error);
      return [];
    }
  }, []);

  // 初始加载
  useEffect(() => {
    loadSessions().then((sessions) => {
      // 尝试从localStorage恢复当前会话
      const savedSessionId = localStorage.getItem('smartsupport_current_session_id');
      if (savedSessionId) {
        // 检查该会话是否仍然存在
        const sessionExists = sessions.some((s) => s.id === savedSessionId);
        if (sessionExists) {
          handleSelectSession(savedSessionId);
        } else {
          // 会话已被删除，清除localStorage
          localStorage.removeItem('smartsupport_current_session_id');
        }
      }
    });
  }, [loadSessions]);

  // 创建新会话
  const handleNewSession = () => {
    const newSessionId = `sess_${generateId()}`;
    const newSession: Session = {
      id: newSessionId,
      title: '新对话',
      timestamp: new Date().toISOString(),
    };
    setSessions((prev) => [newSession, ...prev]);
    setCurrentSessionId(newSessionId);
    localStorage.setItem('smartsupport_current_session_id', newSessionId);
    setMessages([]);
  };

  // 选择会话
  const handleSelectSession = async (id: string) => {
    setCurrentSessionId(id);
    localStorage.setItem('smartsupport_current_session_id', id);
    setMessages([]);

    try {
      const data = await chatApi.getSessionHistory(id);
      const formattedMessages: Message[] = [];

      data.history.forEach((turn, index) => {
        const timestamp = new Date().toISOString();
        formattedMessages.push({
          id: `msg_${index}_user`,
          role: 'user',
          content: turn.user,
          timestamp,
        });
        formattedMessages.push({
          id: `msg_${index}_assistant`,
          role: 'assistant',
          content: turn.assistant,
          timestamp,
        });
      });

      setMessages(formattedMessages);
    } catch (error) {
      console.error('加载会话历史失败:', error);
    }
  };

  // 删除会话
  const handleDeleteSession = async (id: string) => {
    try {
      await chatApi.deleteSession(id);
      setSessions((prev) => prev.filter((s) => s.id !== id));

      if (currentSessionId === id) {
        setCurrentSessionId(undefined);
        setMessages([]);
        localStorage.removeItem('smartsupport_current_session_id');
      }

      antMessage.success('会话已删除');
    } catch (error) {
      antMessage.error('删除会话失败');
    }
  };

  // 发送消息
  const handleSendMessage = async (content: string) => {
    if (!currentSessionId) {
      // 如果没有当前会话，先创建一个
      const newSessionId = `sess_${generateId()}`;
      const newSession: Session = {
        id: newSessionId,
        title: content.slice(0, 20) + (content.length > 20 ? '...' : ''),
        timestamp: new Date().toISOString(),
      };
      setSessions((prev) => [newSession, ...prev]);
      setCurrentSessionId(newSessionId);
      localStorage.setItem('smartsupport_current_session_id', newSessionId);

      // 添加用户消息
      const userMessage: Message = {
        id: generateId(),
        role: 'user',
        content,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage]);

      // 发送请求
      setLoading(true);
      try {
        const response = await chatApi.sendMessage({
          user_id: userId,
          message: content,
          session_id: newSessionId,
        });

        // 添加助手回复
        const assistantMessage: Message = {
          id: generateId(),
          role: 'assistant',
          content: response.reply,
          timestamp: response.timestamp,
          contextCount: response.context_count,
          toolUsed: response.tool_used,
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } catch (error) {
        antMessage.error('发送消息失败，请重试');
        console.error('发送消息失败:', error);
      } finally {
        setLoading(false);
      }
    } else {
      // 添加用户消息
      const userMessage: Message = {
        id: generateId(),
        role: 'user',
        content,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage]);

      // 发送请求
      setLoading(true);
      try {
        const response = await chatApi.sendMessage({
          user_id: userId,
          message: content,
          session_id: currentSessionId,
        });

        // 添加助手回复
        const assistantMessage: Message = {
          id: generateId(),
          role: 'assistant',
          content: response.reply,
          timestamp: response.timestamp,
          contextCount: response.context_count,
          toolUsed: response.tool_used,
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } catch (error) {
        antMessage.error('发送消息失败，请重试');
        console.error('发送消息失败:', error);
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <div className={styles.chatPage}>
      <Sidebar
        sessions={sessions}
        currentSessionId={currentSessionId}
        onNewSession={handleNewSession}
        onSelectSession={handleSelectSession}
        onDeleteSession={handleDeleteSession}
      />
      <div className={styles.chatContainer}>
        <div className={styles.chatHeader}>
          <h2>SmartSupport AI 智能客服</h2>
        </div>
        <MessageList messages={messages} loading={loading} />
        <ChatInput onSend={handleSendMessage} loading={loading} />
      </div>
    </div>
  );
};

export default Chat;
