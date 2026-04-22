import { useState, useEffect, useCallback } from "react";
import { api, Task, TaskStatus } from "./api";

// ─── Estilos inline (sem dependências externas) ───────────────────────────

const S = {
  root: {
    fontFamily: "'Inter', system-ui, sans-serif",
    maxWidth: 720,
    margin: "0 auto",
    padding: "2rem 1rem",
    background: "#f8fafc",
    minHeight: "100vh",
  } as React.CSSProperties,
  header: {
    fontSize: "1.6rem",
    fontWeight: 700,
    color: "#0f172a",
    marginBottom: "1.5rem",
  } as React.CSSProperties,
  card: {
    background: "#fff",
    borderRadius: 12,
    padding: "1.25rem",
    boxShadow: "0 1px 4px rgba(0,0,0,.08)",
    marginBottom: "1rem",
  } as React.CSSProperties,
  row: {
    display: "flex",
    gap: "0.5rem",
    alignItems: "center",
  } as React.CSSProperties,
  input: {
    flex: 1,
    padding: "0.55rem 0.8rem",
    borderRadius: 8,
    border: "1px solid #cbd5e1",
    fontSize: "0.95rem",
    outline: "none",
  } as React.CSSProperties,
  select: {
    padding: "0.55rem 0.6rem",
    borderRadius: 8,
    border: "1px solid #cbd5e1",
    fontSize: "0.85rem",
    background: "#fff",
  } as React.CSSProperties,
  btn: (variant: "primary" | "danger" | "ghost" | "success") => {
    const colors: Record<string, string> = {
      primary: "#6366f1",
      danger:  "#ef4444",
      ghost:   "#94a3b8",
      success: "#22c55e",
    };
    return {
      padding: "0.45rem 0.9rem",
      borderRadius: 8,
      border: "none",
      background: colors[variant],
      color: "#fff",
      cursor: "pointer",
      fontSize: "0.85rem",
      fontWeight: 600,
      transition: "opacity .15s",
    } as React.CSSProperties;
  },
  taskRow: (done: boolean) => ({
    display: "flex",
    alignItems: "center",
    gap: "0.75rem",
    padding: "0.9rem 1rem",
    background: "#fff",
    borderRadius: 10,
    boxShadow: "0 1px 3px rgba(0,0,0,.06)",
    marginBottom: "0.5rem",
    opacity: done ? 0.6 : 1,
  } as React.CSSProperties),
  taskTitle: (done: boolean) => ({
    flex: 1,
    fontSize: "0.95rem",
    textDecoration: done ? "line-through" : "none",
    color: "#0f172a",
  } as React.CSSProperties),
  badge: {
    fontSize: "0.72rem",
    padding: "2px 8px",
    borderRadius: 99,
    background: "#e0e7ff",
    color: "#4338ca",
    fontWeight: 600,
  } as React.CSSProperties,
  filter: {
    display: "flex",
    gap: "0.4rem",
    marginBottom: "1rem",
  } as React.CSSProperties,
  filterBtn: (active: boolean) => ({
    padding: "0.3rem 0.9rem",
    borderRadius: 99,
    border: "1.5px solid",
    borderColor: active ? "#6366f1" : "#cbd5e1",
    background: active ? "#6366f1" : "transparent",
    color: active ? "#fff" : "#64748b",
    cursor: "pointer",
    fontSize: "0.82rem",
    fontWeight: 600,
  } as React.CSSProperties),
  error: {
    color: "#dc2626",
    fontSize: "0.85rem",
    marginTop: "0.4rem",
  } as React.CSSProperties,
};

// ─── Componente principal ─────────────────────────────────────────────────

export default function App() {
  const [tasks, setTasks]         = useState<Task[]>([]);
  const [filter, setFilter]       = useState<"all" | TaskStatus>("all");
  const [newTitle, setNewTitle]   = useState("");
  const [newCategory, setNewCategory] = useState("general");
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState("");

  const load = useCallback(async () => {
    try {
      const data = await api.listTasks(filter === "all" ? undefined : filter);
      setTasks(data);
    } catch {
      setError("Erro ao carregar tarefas.");
    }
  }, [filter]);

  useEffect(() => { load(); }, [load]);

  const handleCreate = async () => {
    if (!newTitle.trim()) { setError("Informe um título."); return; }
    setLoading(true);
    setError("");
    try {
      await api.createTask({ title: newTitle.trim(), category: newCategory });
      setNewTitle("");
      await load();
    } catch {
      setError("Erro ao criar tarefa.");
    } finally {
      setLoading(false);
    }
  };

  const handleComplete = async (id: number) => {
    try {
      await api.completeTask(id);
      await load();
    } catch {
      setError("Erro ao concluir tarefa.");
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await api.deleteTask(id);
      await load();
    } catch {
      setError("Erro ao excluir tarefa.");
    }
  };

  const filters: Array<"all" | TaskStatus> = ["all", "pending", "done"];
  const labels: Record<string, string> = { all: "Todas", pending: "Pendentes", done: "Concluídas" };

  return (
    <div style={S.root}>
      <h1 style={S.header}>📋 Gerenciador de Tarefas</h1>

      {/* Formulário de criação */}
      <div style={S.card}>
        <div style={S.row}>
          <input
            style={S.input}
            placeholder="Nova tarefa…"
            value={newTitle}
            onChange={e => setNewTitle(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleCreate()}
          />
          <select
            style={S.select}
            value={newCategory}
            onChange={e => setNewCategory(e.target.value)}
          >
            {["general", "tech-debt", "quality", "docs", "feature", "bug"].map(c => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
          <button style={S.btn("primary")} onClick={handleCreate} disabled={loading}>
            {loading ? "…" : "Adicionar"}
          </button>
        </div>
        {error && <p style={S.error}>{error}</p>}
      </div>

      {/* Filtros */}
      <div style={S.filter}>
        {filters.map(f => (
          <button key={f} style={S.filterBtn(filter === f)} onClick={() => setFilter(f)}>
            {labels[f]}
          </button>
        ))}
      </div>

      {/* Lista */}
      {tasks.length === 0 && (
        <p style={{ color: "#94a3b8", textAlign: "center", marginTop: "2rem" }}>
          Nenhuma tarefa encontrada.
        </p>
      )}

      {tasks.map(task => (
        <div key={task.id} style={S.taskRow(task.status === "done")}>
          <span style={S.taskTitle(task.status === "done")}>{task.title}</span>
          <span style={S.badge}>{task.category}</span>
          {task.status === "pending" && (
            <button style={S.btn("success")} onClick={() => handleComplete(task.id)}>
              ✓ Concluir
            </button>
          )}
          <button style={S.btn("danger")} onClick={() => handleDelete(task.id)}>
            Excluir
          </button>
        </div>
      ))}
    </div>
  );
}