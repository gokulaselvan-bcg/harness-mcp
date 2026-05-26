import { env } from "../../lib/env";

import {
  TaskListResponseSchema,
  TaskSchema,
  type Task,
  type TaskCreate,
  type TaskUpdate,
} from "./tasksSchemas";

const base = `${env.VITE_API_BASE_URL}/v1/tasks`;

export async function listTasks(): Promise<Task[]> {
  const response = await fetch(base);
  if (!response.ok) {
    throw new Error(`failed to list tasks: ${response.status}`);
  }
  const json = (await response.json()) as unknown;
  return TaskListResponseSchema.parse(json).tasks;
}

export async function createTask(payload: TaskCreate): Promise<Task> {
  const response = await fetch(base, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`failed to create task: ${response.status}`);
  }
  const json = (await response.json()) as unknown;
  return TaskSchema.parse(json);
}

export async function updateTask(id: number, payload: TaskUpdate): Promise<Task> {
  const response = await fetch(`${base}/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`failed to update task ${id}: ${response.status}`);
  }
  const json = (await response.json()) as unknown;
  return TaskSchema.parse(json);
}

export async function deleteTask(id: number): Promise<void> {
  const response = await fetch(`${base}/${id}`, { method: "DELETE" });
  if (!response.ok) {
    throw new Error(`failed to delete task ${id}: ${response.status}`);
  }
}
