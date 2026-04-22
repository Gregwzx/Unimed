// api.ts — Camada de acesso à API

export const API_BASE = "http://localhost:5000";

export type TaskStatus = "pending" | "done";

export interface Task {
  id: number;
  title: string;
  category: string;
  status: TaskStatus;
  createdAt: string;
  completedAt: string | null;
}

export interface CreateTaskPayload {
  title: string;
  category?: string;
}

export interface UpdateTaskPayload {
  title?: string;
  category?: string;
  status?: TaskStatus;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) throw new Error(`HTTP ${res.status} — ${path}`);
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  listTasks: (status?: TaskStatus) =>
    request<Task[]>(`/tasks${status ? `?status=${status}` : ""}`),

  createTask: (payload: CreateTaskPayload) =>
    request<Task>("/tasks", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  updateTask: (id: number, payload: UpdateTaskPayload) =>
    request<Task>(`/tasks/${id}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),

  deleteTask: (id: number) =>
    request<void>(`/tasks/${id}`, { method: "DELETE" }),

  completeTask: (id: number) =>
    request<Task>(`/tasks/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ status: "done" }),
    }),
};