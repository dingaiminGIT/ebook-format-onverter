import React, { useState, useCallback } from 'react';
import {
  Upload,
  Card,
  Select,
  Button,
  Input,
  Form,
  message,
  Progress,
  Space,
  Typography,
  Divider,
  Tag,
} from 'antd';
import {
  InboxOutlined,
  DownloadOutlined,
  FileTextOutlined,
  BookOutlined,
  FilePdfOutlined,
} from '@ant-design/icons';
import { converterApi } from '../services/api';
import { ConversionResponse } from '../types';

const { Dragger } = Upload;
const { Option } = Select;
const { Title, Text } = Typography;

interface FileUploadProps {}

const FileUpload: React.FC<FileUploadProps> = () => {
  const [form] = Form.useForm();
  const [uploading, setUploading] = useState(false);
  const [convertedFile, setConvertedFile] = useState<ConversionResponse | null>(null);
  const [selectedFile, setSelectedFile] = useState<any>(null);
  const [progress, setProgress] = useState(0);

  const formatIcons: { [key: string]: React.ReactNode } = {
    txt: <FileTextOutlined style={{ color: '#1890ff' }} />,
    epub: <BookOutlined style={{ color: '#52c41a' }} />,
    pdf: <FilePdfOutlined style={{ color: '#ff4d4f' }} />,
  };

  const getFileExtension = (filename: string): string => {
    return filename.split('.').pop()?.toLowerCase() || '';
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleFileChange = useCallback((info: any) => {
    const { file } = info;
    console.log('File info:', file); // 调试信息

    // 处理不同的文件对象结构
    const actualFile = file.originFileObj || file;

    if (actualFile && actualFile instanceof File) {
      setSelectedFile(actualFile);
      setConvertedFile(null);
      setProgress(0);
    } else if (file && file.name) {
      // 如果是 Ant Design 的文件对象，但不是原生 File 对象
      setSelectedFile(file);
      setConvertedFile(null);
      setProgress(0);
    }
  }, []);

  const handleConvert = async (values: any) => {
    if (!selectedFile) {
      message.error('请选择要转换的文件');
      return;
    }

    const sourceFormat = getFileExtension(selectedFile.name);
    const { target_format, title, author } = values;

    if (sourceFormat === target_format) {
      message.error('源格式和目标格式相同，无需转换');
      return;
    }

    setUploading(true);
    setProgress(0);

    // 模拟进度条
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return prev;
        }
        return prev + 10;
      });
    }, 200);

    try {
      // 确保传递正确的文件对象
      const fileToUpload = selectedFile?.originFileObj || selectedFile;

      const response = await converterApi.convertFile({
        file: fileToUpload,
        target_format,
        title: title || '转换的电子书',
        author: author || '未知作者',
      });

      clearInterval(progressInterval);
      setProgress(100);
      setConvertedFile(response);
      message.success('转换成功！');
    } catch (error: any) {
      clearInterval(progressInterval);
      setProgress(0);
      message.error(error.response?.data?.detail || '转换失败，请重试');
    } finally {
      setUploading(false);
    }
  };

  const handleDownload = () => {
    if (convertedFile?.download_url) {
      const filename = convertedFile.download_url.split('/').pop() || '';
      const downloadUrl = converterApi.downloadFile(filename);
      window.open(downloadUrl, '_blank');
    }
  };

  const resetForm = () => {
    form.resetFields();
    setSelectedFile(null);
    setConvertedFile(null);
    setProgress(0);
  };

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: '20px' }}>
      <Card>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div style={{ textAlign: 'center' }}>
            <Title level={2}>电子书格式转换器</Title>
            <Text type="secondary">支持 TXT、EPUB、PDF 格式之间的转换</Text>
          </div>

          <Divider />

          <Form form={form} layout="vertical" onFinish={handleConvert}>
            <Form.Item
              label="选择文件"
              name="file"
              rules={[{ required: true, message: '请选择要转换的文件' }]}
            >
              <Dragger
                name="file"
                multiple={false}
                onChange={handleFileChange}
                beforeUpload={() => false} // 阻止自动上传
                accept=".txt,.epub,.pdf"
                disabled={uploading}
              >
                <p className="ant-upload-drag-icon">
                  <InboxOutlined />
                </p>
                <p className="ant-upload-text">点击或拖拽文件到这里上传</p>
                <p className="ant-upload-hint">
                  支持 .txt、.epub、.pdf 格式文件，最大 50MB
                </p>
              </Dragger>
            </Form.Item>

            {selectedFile && (
              <Card size="small" style={{ backgroundColor: '#f6f6f6' }}>
                <Space>
                  {formatIcons[getFileExtension(selectedFile.name)]}
                  <span>{selectedFile.name}</span>
                  <Tag color="blue">{getFileExtension(selectedFile.name).toUpperCase()}</Tag>
                  <span>{formatFileSize(selectedFile.size)}</span>
                </Space>
              </Card>
            )}

            <Form.Item
              label="目标格式"
              name="target_format"
              rules={[{ required: true, message: '请选择目标格式' }]}
            >
              <Select placeholder="选择要转换的目标格式" disabled={uploading}>
                <Option value="txt">
                  <Space>
                    {formatIcons.txt}
                    <span>TXT - 纯文本格式</span>
                  </Space>
                </Option>
                <Option value="epub">
                  <Space>
                    {formatIcons.epub}
                    <span>EPUB - 电子书格式</span>
                  </Space>
                </Option>
                <Option value="pdf">
                  <Space>
                    {formatIcons.pdf}
                    <span>PDF - 便携文档格式</span>
                  </Space>
                </Option>
              </Select>
            </Form.Item>

            <Form.Item label="书籍标题" name="title">
              <Input placeholder="输入书籍标题（可选）" disabled={uploading} />
            </Form.Item>

            <Form.Item label="作者" name="author">
              <Input placeholder="输入作者姓名（可选）" disabled={uploading} />
            </Form.Item>

            {uploading && (
              <Form.Item>
                <Progress
                  percent={progress}
                  status={progress === 100 ? 'success' : 'active'}
                  strokeColor={{
                    '0%': '#108ee9',
                    '100%': '#87d068',
                  }}
                />
              </Form.Item>
            )}

            <Form.Item>
              <Space>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={uploading}
                  disabled={!selectedFile}
                >
                  开始转换
                </Button>
                <Button onClick={resetForm} disabled={uploading}>
                  重置
                </Button>
              </Space>
            </Form.Item>
          </Form>

          {convertedFile && (
            <Card
              title="转换完成"
              style={{ backgroundColor: '#f6ffed', borderColor: '#b7eb8f' }}
            >
              <Space direction="vertical" style={{ width: '100%' }}>
                <Text>{convertedFile.message}</Text>
                {convertedFile.file_size && (
                  <Text type="secondary">
                    文件大小: {formatFileSize(convertedFile.file_size)}
                  </Text>
                )}
                <Button
                  type="primary"
                  icon={<DownloadOutlined />}
                  onClick={handleDownload}
                >
                  下载转换后的文件
                </Button>
              </Space>
            </Card>
          )}

          <Divider />

          <div style={{ textAlign: 'center' }}>
            <Text type="secondary">
              支持的转换: TXT → EPUB, EPUB → PDF
            </Text>
          </div>
        </Space>
      </Card>
    </div>
  );
};

export default FileUpload;