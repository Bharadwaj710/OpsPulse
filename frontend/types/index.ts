export type TaskStatus = 'Pending' | 'In Progress' | 'Completed';

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  avatar_url?: string;
}

export interface Task {
  id: number;
  title: string;
  description: string;
  status: TaskStatus;
  created_by: string;
  created_by_name?: string;
  assigned_to?: string;
  assigned_to_name?: string;
  created_at: string;
  completed_at?: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data: T;
}