export const API_BASE_URL = "http://127.0.0.1:8000";

export async function fetchWithAuth(url: string, options: RequestInit = {}) {
  const token = localStorage.getItem("token");
  const headers = new Headers(options.headers || {});
  
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  
  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    // Optionally trigger a logout event here if token is invalid
    localStorage.removeItem("token");
    window.dispatchEvent(new Event("auth-expired"));
  }

  return response;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  language?: string;
  mode?: string;
  use_web_search?: boolean;
}

export interface ChatSource {
  title: string;
  url: string;
  snippet?: string;
}

export interface ChatResponse {
  content: string;
  session_id: string;
  sources?: ChatSource[];
}

export interface ChallanRequest {
  violation: string;
  state?: string;
  vehicle_type: string;
  repeat: boolean;
}

export interface ChallanResponse {
  violation: string;
  state: string;
  fine_inr: number;
  repeat: boolean;
  section: string;
  explanation: string;
}

export interface ChatSession {
  id: string;
  title: string;
}

export interface ChatHistoryMessage {
  role: string;
  content: string;
  created_at: string;
}

export const chatApi = {
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const res = await fetchWithAuth('/chat', {
      method: 'POST',
      body: JSON.stringify(request)
    });
    if (!res.ok) throw new Error('Failed to send message');
    return res.json();
  },

  async calculateChallan(request: ChallanRequest): Promise<ChallanResponse> {
    const res = await fetchWithAuth('/chat/calculate-challan', {
      method: 'POST',
      body: JSON.stringify(request)
    });
    if (!res.ok) throw new Error('Failed to calculate challan');
    return res.json();
  },

  async getSessions(): Promise<ChatSession[]> {
    const res = await fetchWithAuth('/chat/sessions');
    if (!res.ok) throw new Error('Failed to fetch sessions');
    return res.json();
  },

  async getSessionHistory(sessionId: string): Promise<ChatHistoryMessage[]> {
    const res = await fetchWithAuth(`/chat/history/${sessionId}`);
    if (!res.ok) throw new Error('Failed to fetch history');
    return res.json();
  }
};


