export interface ChatResponse {
  answer: string;
  sql: string | null;
  geojson: any | null;
}

export interface HistoryItem {
  role: 'user' | 'ai';
  content: string;
  sql_query?: string | null;
  geojson?: any | null;
}

export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function getChatHistory(): Promise<HistoryItem[]> {
  const response = await fetch(`${API_URL}/api/history`);
  if (!response.ok) return [];
  return response.json();
}

export async function sendSpatialQuery(message: string): Promise<ChatResponse> {
  const response = await fetch(`${API_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    throw new Error('Failed to fetch from backend API');
  }

  return response.json();
}
