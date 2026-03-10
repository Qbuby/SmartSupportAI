import client from './client';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

export interface ChatRequest {
  user_id: string;
  message: string;
  session_id?: string;
  context?: Record<string, any>;
}

export interface ChatResponse {
  success: boolean;
  reply: string;
  intent?: string;
  tool_used?: string;
  context_count?: number;
  session_id: string;
  timestamp: string;
}

export interface SessionInfo {
  session_id: string;
  user_id: string;
  history_length: number;
  created_at: string;
  last_active: string;
}

export const chatApi = {
  // 发送消息
  sendMessage: (data: ChatRequest): Promise<ChatResponse> => {
    return client.post('/chat', data);
  },

  // 获取会话历史
  getSessionHistory: (sessionId: string): Promise<{ session_id: string; history: any[]; turn_count: number }> => {
    return client.get(`/sessions/${sessionId}/history`);
  },

  // 获取活跃会话列表
  getSessions: (): Promise<SessionInfo[]> => {
    return client.get('/sessions');
  },

  // 删除会话
  deleteSession: (sessionId: string): Promise<{ success: boolean; message: string }> => {
    return client.delete(`/sessions/${sessionId}`);
  },
};
