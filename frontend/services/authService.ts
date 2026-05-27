import { supabase } from "@/lib/supabase";
import { ApiResponse } from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000/api";

export const authService = {
  async syncUser(): Promise<ApiResponse> {
    const { data: { session } } = await supabase.auth.getSession();
    const user = session?.user;
    
    if (!session || !user) {
      return { success: false, message: "No active session found", data: null };
    }

    const response = await fetch(`${API_BASE_URL}/auth/sync`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${session.access_token}`,
      },
      body: JSON.stringify({
        email: user.email,
        name: user.user_metadata.full_name,
        avatar_url: user.user_metadata.avatar_url,
      }),
    });

    return response.json();
  },
};