const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type LoginResponse = {
  access_token: string;
  token_type: string;
};

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("tutorix_token");
}

export function setToken(token: string) {
  localStorage.setItem("tutorix_token", token);
}

export function clearToken() {
  localStorage.removeItem("tutorix_token");
}

export async function api<T = any>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };
  if (token) (headers as any)["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.json();
}

export const auth = {
  login: (email: string, password: string) =>
    api<LoginResponse>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  me: () => api("/api/v1/auth/me"),
};

export const rag = {
  query: (query: string, course_id?: string) =>
    api("/api/v1/rag/query", {
      method: "POST",
      body: JSON.stringify({ query, course_id, top_k: 3 }),
    }),
};

export const questions = {
  generate: (payload: {
    course_id: string;
    topic: string;
    difficulty: string;
    count: number;
    question_type: string;
  }) =>
    api("/api/v1/questions/generate", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
};

export const courses = {
  list: () => api("/api/v1/courses"),
  create: (title: string, description: string) =>
    api("/api/v1/courses", {
      method: "POST",
      body: JSON.stringify({ title, description }),
    }),
};

export const agents = {
  curriculum: (subject: string, grade_level: string, duration_weeks: number) =>
    api("/api/v1/agents/curriculum/generate", {
      method: "POST",
      body: JSON.stringify({ subject, grade_level, duration_weeks }),
    }),
  toolChat: (message: string) =>
    api("/api/v1/agents/tools/chat", {
      method: "POST",
      body: JSON.stringify({ message }),
    }),
};

export const analytics = {
  course: (courseId: string) => api(`/api/v1/analytics/course/${courseId}`),
  student: (studentId: string) =>
    api(`/api/v1/analytics/student/${studentId}`),
};
