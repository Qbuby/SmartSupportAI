import React, { useState } from 'react';
import { Card, Form, InputNumber, Select, Button, message, Slider, Switch } from 'antd';

const { Option } = Select;

const Settings: React.FC = () => {
  const [chunkSize, setChunkSize] = useState(500);
  const [chunkOverlap, setChunkOverlap] = useState(100);
  const [searchType, setSearchType] = useState('hybrid');
  const [vectorTopK, setVectorTopK] = useState(10);
  const [rerankTopK, setRerankTopK] = useState(3);
  const [scoreThreshold, setScoreThreshold] = useState(0.5);
  const [memoryEnabled, setMemoryEnabled] = useState(true);
  const [maxHistoryLength, setMaxHistoryLength] = useState(5);

  const handleSave = () => {
    message.success('配置已保存');
  };

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>策略配置</h2>

      <Card title="Chunk策略" style={{ marginBottom: 24 }}>
        <Form layout="vertical">
          <Form.Item label="Chunk大小">
            <Slider min={100} max={2000} value={chunkSize} onChange={setChunkSize} />
            <InputNumber min={100} max={2000} value={chunkSize} onChange={(v) => setChunkSize(v || 500)} />
          </Form.Item>
          <Form.Item label="Chunk重叠">
            <Slider min={0} max={500} value={chunkOverlap} onChange={setChunkOverlap} />
            <InputNumber min={0} max={500} value={chunkOverlap} onChange={(v) => setChunkOverlap(v || 100)} />
          </Form.Item>
        </Form>
      </Card>

      <Card title="检索策略" style={{ marginBottom: 24 }}>
        <Form layout="vertical">
          <Form.Item label="搜索类型">
            <Select value={searchType} onChange={setSearchType} style={{ width: 200 }}>
              <Option value="vector">向量搜索</Option>
              <Option value="keyword">关键词搜索</Option>
              <Option value="hybrid">混合搜索</Option>
            </Select>
          </Form.Item>
          <Form.Item label="向量检索数量">
            <InputNumber min={1} max={50} value={vectorTopK} onChange={(v) => setVectorTopK(v || 10)} />
          </Form.Item>
          <Form.Item label="重排序TopK">
            <InputNumber min={1} max={20} value={rerankTopK} onChange={(v) => setRerankTopK(v || 3)} />
          </Form.Item>
          <Form.Item label="相关性阈值">
            <Slider min={0} max={1} step={0.1} value={scoreThreshold} onChange={setScoreThreshold} />
          </Form.Item>
        </Form>
      </Card>

      <Card title="记忆策略" style={{ marginBottom: 24 }}>
        <Form layout="vertical">
          <Form.Item label="启用长期记忆">
            <Switch checked={memoryEnabled} onChange={setMemoryEnabled} />
          </Form.Item>
          <Form.Item label="短期记忆长度">
            <InputNumber min={1} max={20} value={maxHistoryLength} onChange={(v) => setMaxHistoryLength(v || 5)} />
          </Form.Item>
        </Form>
      </Card>

      <Button type="primary" size="large" onClick={handleSave}>
        保存配置
      </Button>
    </div>
  );
};

export default Settings;