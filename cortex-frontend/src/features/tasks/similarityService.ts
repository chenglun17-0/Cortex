/**
 * Similarity API Service
 * 任务语义相似度检索
 */
import axios from 'axios';
import { http } from '../../lib/http';

export type SimilarTask = {
  task_id: number;
  title: string;
  description?: string;
  status: string;
  priority: string;
  project_id: number;
  similarity: number;
  created_at?: string;
  recommendation?: string;
};

export type SimilaritySearchResponse = {
  success: boolean;
  query: string;
  results: SimilarTask[];
  total: number;
  message?: string;
};

export type SimilaritySearchParams = {
  text: string;
  exclude_task_id?: number;
  limit?: number;
  threshold?: number;
};

const SIMILARITY_TEXT_MAX_LENGTH = 900;
const DEFAULT_SIMILARITY_ERROR = '服务连接异常，请稍后重试查重';
const SIMILARITY_TIMEOUT_ERROR = '查重请求超时，请缩短标题或描述后重试';

export const buildSimilarityQueryText = (title: string, description?: string): string => {
  const merged = `${title.trim()}\n${(description || '').trim()}`.trim();
  if (merged.length <= SIMILARITY_TEXT_MAX_LENGTH) {
    return merged;
  }
  return merged.slice(0, SIMILARITY_TEXT_MAX_LENGTH);
};

const getAxiosErrorDetail = (error: unknown): string | null => {
  if (!axios.isAxiosError(error)) {
    return null;
  }
  const errorCode = typeof error.code === 'string' ? error.code.toUpperCase() : '';
  if (errorCode === 'ECONNABORTED') {
    return SIMILARITY_TIMEOUT_ERROR;
  }
  const statusCode = error.response?.status;
  if (typeof statusCode === 'number' && statusCode >= 500) {
    return null;
  }

  const detail = error.response?.data?.detail;
  if (typeof detail === 'string') {
    const normalized = detail.trim();
    return normalized.length > 0 ? normalized : null;
  }

  if (Array.isArray(detail)) {
    const firstMessage = detail
      .map((item) => {
        if (!item || typeof item !== 'object') {
          return '';
        }
        const candidate = (item as Record<string, unknown>).msg;
        return typeof candidate === 'string' ? candidate.trim() : '';
      })
      .find((msg) => msg.length > 0);
    return firstMessage || null;
  }

  if (detail && typeof detail === 'object' && typeof (detail as Record<string, unknown>).msg === 'string') {
    const normalized = ((detail as Record<string, unknown>).msg as string).trim();
    return normalized.length > 0 ? normalized : null;
  }

  return null;
};

export const resolveSimilaritySearchErrorMessage = (params: {
  response?: Pick<SimilaritySearchResponse, 'message'>;
  error?: unknown;
} = {}): string => {
  const responseMessage = params.response?.message?.trim();
  if (responseMessage) {
    return responseMessage;
  }

  const axiosDetail = getAxiosErrorDetail(params.error);
  if (axiosDetail) {
    return axiosDetail;
  }

  return DEFAULT_SIMILARITY_ERROR;
};

/**
 * 搜索相似任务
 */
export const searchSimilarTasks = async (params: SimilaritySearchParams): Promise<SimilaritySearchResponse> => {
  const response = await http.post<SimilaritySearchResponse>('/similarity/search', params, {
    timeout: 20000,
  });
  return response.data;
};
