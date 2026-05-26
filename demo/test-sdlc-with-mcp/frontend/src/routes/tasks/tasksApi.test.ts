import { afterAll, afterEach, beforeAll, describe, expect, it } from "vitest";
import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";

import { createTask, deleteTask, listTasks, updateTask } from "./tasksApi";

const server = setupServer();

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

const base = "http://localhost:8000/v1/tasks";

const fakeTask = (overrides: Record<string, unknown> = {}) => ({
  id: 1,
  title: "t",
  description: null,
  completed: false,
  created_at: "2026-05-22T00:00:00",
  updated_at: "2026-05-22T00:00:00",
  ...overrides,
});

describe("listTasks", () => {
  it("returns the parsed array", async () => {
    server.use(
      http.get(base, () =>
        HttpResponse.json({ tasks: [fakeTask({ id: 1, title: "a" })] }),
      ),
    );

    const tasks = await listTasks();

    expect(tasks).toHaveLength(1);
    expect(tasks[0]?.title).toBe("a");
  });

  it("throws on non-2xx", async () => {
    server.use(http.get(base, () => new HttpResponse(null, { status: 500 })));

    await expect(listTasks()).rejects.toThrow(/failed to list tasks/);
  });
});

describe("createTask", () => {
  it("posts JSON and returns the created task", async () => {
    server.use(
      http.post(base, async ({ request }) => {
        const body = (await request.json()) as Record<string, unknown>;
        return HttpResponse.json(
          fakeTask({ id: 7, title: String(body["title"]), description: body["description"] ?? null }),
          { status: 201 },
        );
      }),
    );

    const task = await createTask({ title: "new", description: "d" });

    expect(task.id).toBe(7);
    expect(task.title).toBe("new");
    expect(task.description).toBe("d");
  });

  it("throws on 422", async () => {
    server.use(http.post(base, () => new HttpResponse(null, { status: 422 })));

    await expect(createTask({ title: "" })).rejects.toThrow(/failed to create task/);
  });
});

describe("updateTask", () => {
  it("puts to /{id} and returns the updated task", async () => {
    server.use(
      http.put(`${base}/1`, async ({ request }) => {
        const body = (await request.json()) as Record<string, unknown>;
        return HttpResponse.json(
          fakeTask({ id: 1, completed: Boolean(body["completed"]) }),
        );
      }),
    );

    const task = await updateTask(1, { completed: true });

    expect(task.completed).toBe(true);
  });

  it("throws on 404", async () => {
    server.use(http.put(`${base}/999`, () => new HttpResponse(null, { status: 404 })));

    await expect(updateTask(999, { title: "x" })).rejects.toThrow(/failed to update task 999/);
  });
});

describe("deleteTask", () => {
  it("resolves on 204", async () => {
    server.use(http.delete(`${base}/1`, () => new HttpResponse(null, { status: 204 })));

    await expect(deleteTask(1)).resolves.toBeUndefined();
  });

  it("throws on 404", async () => {
    server.use(http.delete(`${base}/1`, () => new HttpResponse(null, { status: 404 })));

    await expect(deleteTask(1)).rejects.toThrow(/failed to delete task 1/);
  });
});
