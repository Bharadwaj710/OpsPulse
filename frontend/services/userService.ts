import { supabase } from "@/lib/supabase";
import { UserProfile, ApiResponse } from "@/types";

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

export const userService = {
  async getUsers(): Promise<ApiResponse<UserProfile[]>> {
    return fetchWithAuth("/users");
  },
};
