import { useEffect, useState, type FormEvent } from "react";
import { api, type Task } from "./api";

export default function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    try {
      setTasks(await api.list());
    } catch (e) {
      setError(String(e));
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    if (!title.trim()) return;
    try {
      await api.create({ title: title.trim(), description });
      setTitle("");
      setDescription("");
      await refresh();
    } catch (e) {
      setError(String(e));
    }
  }

  async function toggleComplete(task: Task) {
    await api.update(task.id, { completed: !task.completed });
    await refresh();
  }

  async function remove(id: number) {
    await api.remove(id);
    await refresh();
  }

  function startEdit(task: Task) {
    setEditingId(task.id);
    setEditTitle(task.title);
    setEditDescription(task.description);
  }

  async function saveEdit(id: number) {
    await api.update(id, { title: editTitle, description: editDescription });
    setEditingId(null);
    await refresh();
  }

  return (
    <main className="container">
      <h1>Task Manager</h1>
      {error && <div className="error">{error}</div>}

      <form className="create-form" onSubmit={handleCreate}>
        <input
          placeholder="Task title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <input
          placeholder="Description (optional)"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        <button type="submit">Add</button>
      </form>

      <ul className="task-list">
        {tasks.map((task) => (
          <li key={task.id} className={task.completed ? "done" : ""}>
            <input
              type="checkbox"
              checked={task.completed}
              onChange={() => toggleComplete(task)}
            />
            {editingId === task.id ? (
              <div className="edit-row">
                <input
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                />
                <input
                  value={editDescription}
                  onChange={(e) => setEditDescription(e.target.value)}
                />
                <button onClick={() => saveEdit(task.id)}>Save</button>
                <button onClick={() => setEditingId(null)}>Cancel</button>
              </div>
            ) : (
              <div className="task-row">
                <div className="task-text">
                  <strong>{task.title}</strong>
                  {task.description && <span> — {task.description}</span>}
                </div>
                <button onClick={() => startEdit(task)}>Edit</button>
                <button onClick={() => remove(task.id)}>Delete</button>
              </div>
            )}
          </li>
        ))}
        {tasks.length === 0 && <li className="empty">No tasks yet.</li>}
      </ul>
    </main>
  );
}
