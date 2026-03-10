import client from './client';

export interface Document {
  id: string;
  filename: string;
  original_name: string;
  file_type: string;
  size: number;
  status: 'pending' | 'processing' | 'indexed' | 'error';
  chunk_count?: number;
  created_at: string;
  updated_at: string;
}

export interface DocumentListResponse {
  total: number;
  items: Document[];
  page: number;
  page_size: number;
}

export const documentApi = {
  // 获取文档列表
  getList: async (page: number = 1, pageSize: number = 20): Promise<DocumentListResponse> => {
    const response = await client.get(`/api/admin/documents?page=${page}&page_size=${pageSize}`);
    return response;
  },

  // 获取文档详情
  getById: async (id: string): Promise<Document> => {
    const response = await client.get(`/api/admin/documents/${id}`);
    return response;
  },

  // 获取文档内容
  getContent: async (id: string): Promise<{ content: string; type: string }> => {
    const response = await client.get(`/api/admin/documents/${id}/content`);
    return response;
  },

  // 删除文档
  delete: async (id: string): Promise<{ message: string; doc_id: string }> => {
    const response = await client.delete(`/api/admin/documents/${id}`);
    return response;
  },

  // 重新索引
  reindex: async (id: string): Promise<{ message: string; doc_id: string }> => {
    const response = await client.post(`/api/admin/documents/${id}/reindex`);
    return response;
  },

  // 上传文档（返回FormData配置）
  getUploadConfig: () => ({
    action: `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/admin/documents/upload`,
    headers: {
      // 如需认证token，在这里添加
    },
  }),
};
