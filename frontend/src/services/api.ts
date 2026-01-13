import axios from 'axios';
import { ConversionResponse, SupportedFormat, ConversionRequest } from '../types';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30秒超时
});

export const converterApi = {
  // 获取支持的格式
  getSupportedFormats: async (): Promise<SupportedFormat> => {
    const response = await api.get('/formats');
    return response.data;
  },

  // 转换文件
  convertFile: async (request: ConversionRequest): Promise<ConversionResponse> => {
    const formData = new FormData();
    formData.append('file', request.file);
    formData.append('target_format', request.target_format);
    if (request.title) {
      formData.append('title', request.title);
    }
    if (request.author) {
      formData.append('author', request.author);
    }

    const response = await api.post('/convert', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  // 下载文件
  downloadFile: (filename: string): string => {
    return `${API_BASE_URL}/download/${filename}`;
  },

  // 清理文件
  cleanupFile: async (filename: string): Promise<void> => {
    await api.delete(`/cleanup/${filename}`);
  },
};

export default api;