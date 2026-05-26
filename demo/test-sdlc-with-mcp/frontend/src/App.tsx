import { Tasks } from "./routes/tasks/Tasks";

export function App() {
  return (
    <main style={{ maxWidth: 720, margin: "2rem auto", padding: "0 1rem", fontFamily: "system-ui" }}>
      <h1>Task Manager</h1>
      <Tasks />
    </main>
  );
}
