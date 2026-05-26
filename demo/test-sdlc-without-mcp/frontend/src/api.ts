export type Task = {
  id: number;
  title: string;
  description: string;
  completed: boolean;
  created_at: string;
};

export type TaskCreate = {
  title: string;
  description?: string;
  completed?: boolean;
};

export type TaskUpdate = Partial<TaskCreate>;

const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    throw new Error(`${res.status} ${res.statusText}`);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  list: () => request<Task[]>("/tasks"),
  get: (id: number) => request<Task>(`/tasks/${id}`),
  create: (body: TaskCreate) =>
    request<Task>("/tasks", { method: "POST", body: JSON.stringify(body) }),
  update: (id: number, body: TaskUpdate) =>
    request<Task>(`/tasks/${id}`, {
      method: "PUT",
      body: JSON.stringify(body),
    }),
  remove: (id: number) =>
    request<void>(`/tasks/${id}`, { method: "DELETE" }),
};
