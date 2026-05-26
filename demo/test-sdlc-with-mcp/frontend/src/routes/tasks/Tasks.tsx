import { useEffect, useState, type FormEvent } from "react";

import { createTask, deleteTask, listTasks, updateTask } from "./tasksApi";
import type { Task } from "./tasksSchemas";

export function Tasks() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newTitle, setNewTitle] = useState("");
  const [newDescription, setNewDescription] = useState("");

  useEffect(() => {
    void (async () => {
      try {
        setTasks(await listTasks());
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load tasks");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (newTitle.trim() === "") return;
    try {
      const trimmedDescription = newDescription.trim();
      const created = await createTask({
        title: newTitle.trim(),
        ...(trimmedDescription === "" ? {} : { description: trimmedDescription }),
      });
      setTasks((prev) => [...prev, created]);
      setNewTitle("");
      setNewDescription("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create task");
    }
  }

  async function handleToggle(task: Task) {
    try {
      const updated = await updateTask(task.id, { completed: !task.completed });
      setTasks((prev) => prev.map((t) => (t.id === updated.id ? updated : t)));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to update task");
    }
  }

  async function handleDelete(taskId: number) {
    try {
      await deleteTask(taskId);
      setTasks((prev) => prev.filter((t) => t.id !== taskId));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to delete task");
    }
  }

  if (loading) {
    return <p>Loading…</p>;
  }

  return (
    <section>
      {error !== null ? (
        <p role="alert" style={{ color: "crimson" }}>
          {error}
        </p>
      ) : null}

      <form onSubmit={handleCreate} style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        <input
          aria-label="Title"
          placeholder="Title"
          value={newTitle}
          onChange={(e) => setNewTitle(e.target.value)}
          required
        />
        <input
          aria-label="Description"
          placeholder="Description (optional)"
          value={newDescription}
          onChange={(e) => setNewDescription(e.target.value)}
        />
        <button type="submit">Add task</button>
      </form>

      {tasks.length === 0 ? (
        <p>No tasks yet.</p>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {tasks.map((task) => (
            <li
              key={task.id}
              style={{ display: "flex", gap: 8, alignItems: "center", padding: "4px 0" }}
            >
              <label style={{ display: "flex", gap: 8, alignItems: "center", flex: 1 }}>
                <input
                  type="checkbox"
                  checked={task.completed}
                  onChange={() => {
                    void handleToggle(task);
                  }}
                />
                <span
                  style={{
                    textDecoration: task.completed ? "line-through" : "none",
                    color: task.completed ? "#888" : "inherit",
                  }}
                >
                  {task.title}
                </span>
                {task.description !== null && task.description !== "" ? (
                  <span style={{ color: "#666" }}>— {task.description}</span>
                ) : null}
              </label>
              <button
                type="button"
                aria-label={`Delete ${task.title}`}
                onClick={() => {
                  void handleDelete(task.id);
                }}
              >
                Delete
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
