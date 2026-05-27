import { supabase } from "@/lib/supabase";
import { Task, ApiResponse } from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:5000/api";

async function fetchWithAuth(endpoint: string, options: RequestInit = {}) {
  const { data: { session } } = await supabase.auth.getSession();
  const token = session?.access_token;

  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
    Authorization: `Bearer ${token}`,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });
  return response.json();
}

export const taskService = {
  async getTasks(): Promise<ApiResponse<Task[]>> {
    return fetchWithAuth("/tasks");
  },

  async createTask(taskData: Partial<Task>): Promise<ApiResponse> {
    return fetchWithAuth("/tasks", {
      method: "POST",
      body: JSON.stringify(taskData),
    });
  },

  async updateStatus(id: number, status: Task['status']): Promise<ApiResponse> {
    return fetchWithAuth("/tasks/status", {
      method: "PATCH",
      body: JSON.stringify({ id, status }),
    });
  },

  async deleteTask(id: number): Promise<ApiResponse> {
    return fetchWithAuth(`/tasks/${id}`, {
      method: "DELETE",
    });
  },

  async updateTask(id: number, taskData: Partial<Task>): Promise<ApiResponse> {
    return fetchWithAuth(`/tasks/${id}`, {
      method: "PUT",
      body: JSON.stringify(taskData),
    });
  },

  async getActivities(): Promise<ApiResponse<any[]>> {
    return fetchWithAuth("/tasks/activities");
  },
};