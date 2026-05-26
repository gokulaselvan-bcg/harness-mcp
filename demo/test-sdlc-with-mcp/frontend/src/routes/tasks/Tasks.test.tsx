import { afterAll, afterEach, beforeAll, describe, expect, it } from "vitest";
import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { Tasks } from "./Tasks";

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

const server = setupServer();

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe("Tasks", () => {
  it("renders an empty state when there are no tasks", async () => {
    server.use(http.get(base, () => HttpResponse.json({ tasks: [] })));

    render(<Tasks />);

    expect(await screen.findByText("No tasks yet.")).toBeInTheDocument();
  });

  it("renders existing tasks from the API", async () => {
    server.use(
      http.get(base, () =>
        HttpResponse.json({
          tasks: [
            fakeTask({ id: 1, title: "buy milk" }),
            fakeTask({ id: 2, title: "walk dog", completed: true }),
          ],
        }),
      ),
    );

    render(<Tasks />);

    expect(await screen.findByText("buy milk")).toBeInTheDocument();
    expect(screen.getByText("walk dog")).toBeInTheDocument();
  });

  it("creates a new task and appends it to the list", async () => {
    server.use(
      http.get(base, () => HttpResponse.json({ tasks: [] })),
      http.post(base, async ({ request }) => {
        const body = (await request.json()) as Record<string, unknown>;
        return HttpResponse.json(
          fakeTask({ id: 10, title: String(body["title"]) }),
          { status: 201 },
        );
      }),
    );
    const user = userEvent.setup();

    render(<Tasks />);
    await screen.findByText("No tasks yet.");

    await user.type(screen.getByLabelText("Title"), "write README");
    await user.click(screen.getByRole("button", { name: /add task/i }));

    expect(await screen.findByText("write README")).toBeInTheDocument();
  });

  it("toggles a task's completion", async () => {
    server.use(
      http.get(base, () =>
        HttpResponse.json({ tasks: [fakeTask({ id: 5, title: "t", completed: false })] }),
      ),
      http.put(`${base}/5`, async () =>
        HttpResponse.json(fakeTask({ id: 5, title: "t", completed: true })),
      ),
    );
    const user = userEvent.setup();

    render(<Tasks />);
    const checkbox = await screen.findByRole("checkbox");

    await user.click(checkbox);

    await waitFor(() => {
      expect(checkbox).toBeChecked();
    });
  });

  it("removes a deleted task from the list", async () => {
    server.use(
      http.get(base, () =>
        HttpResponse.json({ tasks: [fakeTask({ id: 9, title: "doomed" })] }),
      ),
      http.delete(`${base}/9`, () => new HttpResponse(null, { status: 204 })),
    );
    const user = userEvent.setup();

    render(<Tasks />);
    await screen.findByText("doomed");

    await user.click(screen.getByRole("button", { name: /delete doomed/i }));

    await waitFor(() => {
      expect(screen.queryByText("doomed")).not.toBeInTheDocument();
    });
  });

  it("shows an error when load fails", async () => {
    server.use(http.get(base, () => new HttpResponse(null, { status: 500 })));

    render(<Tasks />);

    expect(await screen.findByRole("alert")).toHaveTextContent(/failed to list tasks/i);
  });
});
