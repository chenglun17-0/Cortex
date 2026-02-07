/**
 * Similarity API Service
 * 任务语义相似度检索
 */
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

/**
 * 搜索相似任务
 */
export const searchSimilarTasks = async (params: SimilaritySearchParams): Promise<SimilaritySearchResponse> => {
  const response = await http.post<SimilaritySearchResponse>('/similarity/search', params);
  return response.data;
};
