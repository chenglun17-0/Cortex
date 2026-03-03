import { http } from '../../lib/http';

export interface CountItem {
  key: string;
  count: number;
}

export interface OverviewReport {
  total_projects: number;
  total_tasks: number;
  completed_tasks: number;
  completion_rate: number;
  status_distribution: CountItem[];
  priority_distribution: CountItem[];
}

export const getOverviewReport = async (): Promise<OverviewReport> => {
  const response = await http.get<OverviewReport>('/reports/overview');
  return response.data;
};
