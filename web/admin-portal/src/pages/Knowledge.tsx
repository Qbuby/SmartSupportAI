import React, { useState } from 'react';
import { Table, Button, Upload, message, Space } from 'antd';
import { UploadOutlined, DeleteOutlined, EyeOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd';

interface Document {
  id: string;
  name: string;
  size: string;
  status: 'processing' | 'indexed' | 'error';
  uploadTime: string;
}

const Knowledge: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([
    { id: '1', name: '产品手册.pdf', size: '2.5MB', status: 'indexed', uploadTime: '2025-03-10' },
    { id: '2', name: 'API文档.md', size: '156KB', status: 'indexed', uploadTime: '2025-03-09' },
  ]);

  const uploadProps: UploadProps = {
    name: 'file',
    action: 'http://localhost:8000/api/admin/documents/upload',
    headers: {
      authorization: 'admin-token',
    },
    onChange(info) {
      if (info.file.status === 'done') {
        message.success(`${info.file.name} 上传成功`);
      } else if (info.file.status === 'error') {
        message.error(`${info.file.name} 上传失败`);
      }
    },
  };

  const columns = [
    { title: '文件名', dataIndex: 'name', key: 'name' },
    { title: '大小', dataIndex: 'size', key: 'size' },
    { title: '状态', dataIndex: 'status', key: 'status', render: (s: string) => s === 'indexed' ? '已索引' : '处理中' },
    { title: '上传时间', dataIndex: 'uploadTime', key: 'uploadTime' },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Document) => (
        <Space>
          <Button icon={<EyeOutlined />} size="small">预览</Button>
          <Button icon={<DeleteOutlined />} danger size="small" onClick={() => {
            setDocuments(docs => docs.filter(d => d.id !== record.id));
            message.success('已删除');
          }}>删除</Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>知识库管理</h2>

      <div style={{ marginBottom: 16 }}>
        <Upload {...uploadProps}>
          <Button icon={<UploadOutlined />}>上传文档</Button>
        </Upload>
      </div>

      <Table columns={columns} dataSource={documents} rowKey="id" />
    </div>
  );
};

export default Knowledge;
